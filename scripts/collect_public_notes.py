#!/usr/bin/env python3
"""
collect_public_notes.py — Public notes collector for the Quarto notes website.

Scans the Obsidian vault for notes with `public: true` frontmatter and copies
them into notes/, injecting path-based tags and rewriting inter-note links.

Text transformations (callouts, mermaid) are handled at render time by
gfm_to_quarto_filter.lua, applied globally via _quarto.yml.

Invoked as a Quarto pre-render hook — run from 07_Quarto_Notes/.
Replaces scripts/batch_gfm_to_quarto.py (now deprecated).

No third-party dependencies — stdlib only.
"""

import os
import re
import shutil
from pathlib import Path
from urllib.parse import unquote


# ---------------------------------------------------------------------------
# Paths (resolved relative to this file's location)
# ---------------------------------------------------------------------------
SCRIPT_DIR    = Path(__file__).resolve().parent   # 07_Quarto_Notes/scripts/
PROJECT_DIR   = SCRIPT_DIR.parent                 # 07_Quarto_Notes/
VAULT_ROOT    = PROJECT_DIR.parent                # notesSynced/
LEGACY_DIR    = PROJECT_DIR / "_notes"            # legacy staging area
OUTPUT_DIR    = PROJECT_DIR / "notes"             # flat .qmd output directory
OUTPUT_ATTACH = OUTPUT_DIR / "attachments"        # merged attachments directory


# ---------------------------------------------------------------------------
# Scan configuration
#
# Each entry: (root_path, excluded_dir_names, derive_path_tags)
#   root_path          – top of the directory tree to walk
#   excluded_dir_names – set of directory names (not full paths) never descended into
#   derive_path_tags   – whether to inject path-hierarchy tags into frontmatter
#
# The vault-wide scan is only added when VAULT_ROOT contains a .obsidian/
# directory, confirming this project lives inside an Obsidian vault.
# When that marker is absent (CI, standalone clone), the scan is skipped
# gracefully and only _notes/ is processed.
# ---------------------------------------------------------------------------
SCAN_ROOTS = []

if (VAULT_ROOT / ".obsidian").is_dir():
    SCAN_ROOTS.append((
        VAULT_ROOT,
        {
            "07_Quarto_Notes",   # output repo — avoid feedback loop
            ".obsidian",
            ".git",
            ".stfolder",
            "98-Scripts",
            "banyan_config",
            "Notion",
            "05-for-agents",
        },
        True,   # inject path-based tags
    ))

SCAN_ROOTS.append((
    LEGACY_DIR,
    set(),
    False,  # _notes/ has no meaningful path hierarchy for tags
))

TARGET_EXTENSIONS = {".md", ".qmd", ".rmd", ".markdown"}


# ---------------------------------------------------------------------------
# Compiled regex patterns
# ---------------------------------------------------------------------------

# YAML frontmatter block anchored to the very start of a file.
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---[ \t]*(?:\n|$)", re.DOTALL)

# `public: true` (and common YAML truthy aliases) on its own line.
PUBLIC_RE = re.compile(
    r"^public\s*:\s*(true|yes|on)\s*(?:#.*)?$",
    re.MULTILINE | re.IGNORECASE,
)

# Block-style tags list:
#   tags:
#     - Foo
#     - Bar
TAGS_BLOCK_RE = re.compile(
    r"^(tags\s*:[ \t]*\n(?:[ \t]+-[^\n]*\n?)*)",
    re.MULTILINE,
)

# Flow-style tags list:  tags: [Foo, Bar]
TAGS_FLOW_RE = re.compile(
    r"^(tags\s*:\s*\[[^\]]*\])[ \t]*$",
    re.MULTILINE,
)

# Markdown link to a note file (negative lookbehind excludes image links).
# Negative lookahead excludes URLs with a scheme (https://, http://, ftp://, etc.)
# so that external links whose URLs happen to end in .md are not rewritten.
NOTE_LINK_RE = re.compile(
    r"(?<!!)\[([^\]]*)\]\((?![a-zA-Z][a-zA-Z0-9+\-.]*://)([^)]*?\.(?:md|qmd|rmd|markdown))(?:[#?][^)]*)?\)",
    re.IGNORECASE,
)

# Folder naming convention: leading "03_"-style prefix.
NUMBER_PREFIX_RE = re.compile(r"^\d+_")

# Detects an existing `title:` key anywhere in the YAML block.
TITLE_RE = re.compile(r"^title\s*:", re.MULTILINE)

# Detects an existing `from:` key (Pandoc reader override) in the YAML block.
FROM_RE = re.compile(r"^from\s*:", re.MULTILINE)

# GFM bullet / ordered-list line marker (used by ensure_list_blank_lines).
_LIST_MARKER_RE = re.compile(r"^(?:[-*+]|\d+[.)]) ")

# Fenced code-block delimiter (3+ identical fence chars at the start of a line).
_FENCE_RE = re.compile(r"^([`~])\1{2,}")


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def split_frontmatter(text: str) -> tuple[str | None, str]:
    """
    Split a file into (raw_yaml_string, body_string).
    Returns (None, text) when no frontmatter block is found.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    raw_yaml = m.group(1)
    body = text[m.end():]
    return raw_yaml, body


def is_public(raw_yaml: str) -> bool:
    """Return True only when `public: true` (or a truthy YAML alias) is present."""
    return bool(PUBLIC_RE.search(raw_yaml))


# ---------------------------------------------------------------------------
# Tag derivation and injection
# ---------------------------------------------------------------------------

def _clean_segment(segment: str) -> str:
    """
    Convert a vault folder name into a readable tag.
      "03_Concepts"  →  "Concepts"
      "My_Topic"     →  "My Topic"
    Hidden / system segments (starting with '.') return an empty string.
    """
    if segment.startswith("."):
        return ""
    cleaned = NUMBER_PREFIX_RE.sub("", segment)
    return cleaned.replace("_", " ").title()


def derive_tags(file_path: Path, root: Path) -> list[str]:
    """
    Build a tag list from the directory components between root and file_path.

    Example:
      notesSynced/03_Concepts/Physics/note.md  →  ["Concepts", "Physics"]
    """
    try:
        rel = file_path.relative_to(root)
    except ValueError:
        return []
    tags = [_clean_segment(p) for p in rel.parent.parts]
    return [t for t in tags if t]


def _parse_existing_tags(raw_yaml: str) -> list[str]:
    """Extract tag values from a block-style or flow-style YAML `tags:` key."""
    m = TAGS_BLOCK_RE.search(raw_yaml)
    if m:
        tags = []
        for line in m.group(1).splitlines():
            stripped = line.strip()
            if stripped.startswith("-"):
                tag = stripped[1:].strip().strip("\"'")
                if tag:
                    tags.append(tag)
        return tags

    m = TAGS_FLOW_RE.search(raw_yaml)
    if m:
        inner = re.search(r"\[([^\]]*)\]", m.group(1))
        if inner:
            return [t.strip().strip("\"'") for t in inner.group(1).split(",") if t.strip()]

    return []


def _build_tags_block(tags: list[str]) -> str:
    """Render a canonical block-style YAML tags list."""
    return "tags:\n" + "".join(f"  - {t}\n" for t in tags)


def inject_title(raw_yaml: str, stem: str) -> str:
    """
    Prepend `title: "<stem>"` to raw_yaml when no title key is present.
    The stem is the Obsidian note filename without extension, which is the
    canonical note title in an Obsidian vault.
    """
    if TITLE_RE.search(raw_yaml):
        return raw_yaml  # title already set — leave it alone
    quoted = stem.replace('"', '\\"')
    return f'title: "{quoted}"\n' + raw_yaml


def inject_from_gfm(raw_yaml: str) -> str:
    """
    Prepend `from: markdown+lists_without_preceding_blankline` when no `from:`
    key is present.

    Stays on Pandoc's standard `markdown` reader (which Quarto requires for
    fenced_divs and other extensions it injects at render time) while adding
    the single GFM extension that allows lists to interrupt paragraphs and
    blockquotes without a preceding blank line — matching Obsidian's behaviour.
    """
    if FROM_RE.search(raw_yaml):
        return raw_yaml  # reader already overridden — leave it alone
    return "from: markdown+lists_without_preceding_blankline\n" + raw_yaml


def inject_tags(raw_yaml: str, new_tags: list[str]) -> str:
    """
    Merge new_tags into the existing `tags:` list in raw_yaml via string
    manipulation (no YAML library required; original formatting is preserved
    for all keys other than `tags:`).

    Returns raw_yaml unchanged when new_tags is empty.
    """
    if not new_tags:
        return raw_yaml

    existing = _parse_existing_tags(raw_yaml)
    merged = existing + [t for t in new_tags if t not in existing]
    new_block = _build_tags_block(merged)

    # Replace an existing block-style tags key.
    m = TAGS_BLOCK_RE.search(raw_yaml)
    if m:
        return raw_yaml[: m.start()] + new_block + raw_yaml[m.end():]

    # Replace an existing flow-style tags key.
    m = TAGS_FLOW_RE.search(raw_yaml)
    if m:
        return raw_yaml[: m.start()] + new_block.rstrip("\n") + raw_yaml[m.end():]

    # Append when no `tags:` key exists yet.
    return raw_yaml.rstrip("\n") + "\n" + new_block


# ---------------------------------------------------------------------------
# Link rewriting
# ---------------------------------------------------------------------------

def _rewrite_link(m: re.Match) -> str:
    """Replace a note link's target with a flat <stem>.qmd reference."""
    display = m.group(1)
    raw_target = m.group(2)
    stem = Path(unquote(raw_target)).stem   # URL-decode, then take the filename stem
    return f"[{display}]({stem}.qmd)"


def rewrite_links(body: str) -> str:
    """Rewrite all markdown links that point to note files (→ flat <stem>.qmd)."""
    return NOTE_LINK_RE.sub(_rewrite_link, body)


# ---------------------------------------------------------------------------
# List blank-line normalization
# ---------------------------------------------------------------------------

def _is_list_marker(line: str) -> bool:
    """Return True when line begins with a GFM bullet or ordered list marker."""
    return bool(_LIST_MARKER_RE.match(line))


def ensure_list_blank_lines(body: str) -> str:
    """
    Insert a blank line before GFM list markers that immediately follow a
    non-blank, non-list line.

    Pandoc's markdown reader requires this separator; Obsidian/GFM does not.
    Fenced code blocks (``` or ~~~) are passed through unchanged so that
    shell-command lines or other content starting with '-' are not mangled.
    """
    lines = body.split("\n")
    result: list[str] = []
    in_fence = False
    fence_char = ""

    for line in lines:
        stripped = line.lstrip()
        leading = len(line) - len(stripped)

        # Track fenced code blocks (CommonMark: at most 3 spaces of indent).
        if leading <= 3:
            m = _FENCE_RE.match(stripped)
            if m:
                ch = m.group(1)
                after = stripped[len(m.group(0)):]
                if not in_fence:
                    in_fence = True
                    fence_char = ch
                elif ch == fence_char and not after.strip():
                    # Closing fence: same char, no trailing non-space content.
                    in_fence = False

        if not in_fence and result and _is_list_marker(stripped):
            prev_stripped = result[-1].strip()
            if prev_stripped and not _is_list_marker(prev_stripped):
                result.append("")

        result.append(line)

    return "\n".join(result)


# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------

def smart_write(dest: Path, content: str) -> bool:
    """
    Write content to dest only when it differs from the existing file.
    Returns True if the file was (over)written, False if skipped.
    Preserving unchanged files protects Quarto's freeze: auto cache.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.read_text(encoding="utf-8") == content:
        return False
    dest.write_text(content, encoding="utf-8")
    return True


def copy_attachments(
    src_note: Path,
    seen_files: set[str],
    seen_dirs: set[Path],
) -> None:
    """
    Merge the attachments/ directory adjacent to src_note into OUTPUT_ATTACH.

    seen_dirs prevents re-scanning the same source directory when multiple
    notes in the same folder share one attachments/ (e.g. all of _notes/).
    seen_files detects genuine filename collisions across different source dirs.
    """
    src_dir = src_note.parent / "attachments"
    if not src_dir.is_dir() or src_dir in seen_dirs:
        return
    seen_dirs.add(src_dir)

    OUTPUT_ATTACH.mkdir(parents=True, exist_ok=True)
    for item in sorted(src_dir.iterdir()):
        if not item.is_file():
            continue
        if item.name in seen_files:
            print(
                f"  [WARN] Attachment collision, skipping '{item.name}' "
                f"(from {src_dir})"
            )
            continue
        seen_files.add(item.name)
        shutil.copyfile(item, OUTPUT_ATTACH / item.name)


# ---------------------------------------------------------------------------
# Stale file pruning
# ---------------------------------------------------------------------------

def prune_stale(expected_stems: set[str]) -> int:
    """
    Delete .qmd files in OUTPUT_DIR whose stems are absent from expected_stems.
    Returns the count of removed files.
    """
    removed = 0
    for qmd in OUTPUT_DIR.glob("*.qmd"):
        if qmd.stem not in expected_stems:
            qmd.unlink()
            print(f"  Pruned stale: {qmd.name}")
            removed += 1
    return removed


# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------

def scan_root(
    root: Path,
    exclude_names: set[str],
    derive_path_tags: bool,
    expected_stems: set[str],
    seen_stems: set[str],
    seen_attachment_files: set[str],
    seen_attachment_dirs: set[Path],
) -> tuple[int, int]:
    """
    Walk root, find notes with `public: true`, and copy them to OUTPUT_DIR.
    Returns (processed_count, skipped_count).
    """
    processed = skipped = 0

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded and hidden directories in-place (controls os.walk descent).
        dirnames[:] = [
            d for d in dirnames
            if d not in exclude_names and not d.startswith(".")
        ]

        for filename in sorted(filenames):
            src = Path(dirpath) / filename
            if src.suffix.lower() not in TARGET_EXTENSIONS:
                continue

            try:
                text = src.read_text(encoding="utf-8")
            except OSError as exc:
                print(f"  [WARN] Cannot read {src}: {exc}")
                continue

            raw_yaml, body = split_frontmatter(text)
            if raw_yaml is None or not is_public(raw_yaml):
                continue   # no frontmatter or not marked public → skip

            stem = src.stem

            # Collision check across all scan roots.
            if stem in seen_stems:
                print(
                    f"  [WARN] Filename collision — skipping "
                    f"'{src.relative_to(VAULT_ROOT)}' "
                    f"('{stem}.qmd' already queued)"
                )
                skipped += 1
                continue

            seen_stems.add(stem)
            expected_stems.add(stem)

            # Inject title from the filename stem when none is set.
            raw_yaml = inject_title(raw_yaml, stem)

            # Tell Pandoc to parse the body as GFM so that lists can interrupt
            # paragraphs (and blockquotes) without requiring a blank line —
            # matching Obsidian's rendering behaviour.
            raw_yaml = inject_from_gfm(raw_yaml)

            # Inject path-hierarchy tags (vault-wide scan only).
            if derive_path_tags:
                new_tags = derive_tags(src, root)
                raw_yaml = inject_tags(raw_yaml, new_tags)

            # Rewrite inter-note markdown links to flat .qmd targets.
            body = rewrite_links(body)

            # Reconstruct the full file content.
            content = "---\n" + raw_yaml.rstrip() + "\n---\n\n" + body.lstrip("\n")

            dest = OUTPUT_DIR / f"{stem}.qmd"
            written = smart_write(dest, content)
            if written:
                try:
                    label = src.relative_to(VAULT_ROOT)
                except ValueError:
                    label = src
                print(f"  Copied:  {label}  ->  notes/{stem}.qmd")

            copy_attachments(src, seen_attachment_files, seen_attachment_dirs)
            processed += 1

    return processed, skipped


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    # Whether the project lives inside the Obsidian vault.
    # When False (CI, standalone clone), the vault-wide scan is skipped and
    # prune_stale is suppressed so that vault-wide notes committed locally are
    # not removed from the deployed site.
    vault_present = (VAULT_ROOT / ".obsidian").is_dir()
    if not vault_present:
        print("No Obsidian vault detected — running in CI/standalone mode.")
        print("Vault-wide scan skipped; vault-sourced notes in notes/ preserved.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Clear attachments at the start of every run so stale files from removed
    # notes don't linger.  Quarto freeze: auto is unaffected (it tracks .qmd
    # execution outputs, not static attachment files).
    if OUTPUT_ATTACH.exists():
        shutil.rmtree(OUTPUT_ATTACH)
    OUTPUT_ATTACH.mkdir()

    expected_stems:        set[str]  = set()
    seen_stems:            set[str]  = set()
    seen_attachment_files: set[str]  = set()
    seen_attachment_dirs:  set[Path] = set()

    total_processed = total_skipped = 0

    for root, exclude_names, derive_path_tags in SCAN_ROOTS:
        if not root.exists():
            print(f"[WARN] Scan root not found, skipping: {root}")
            continue
        try:
            label = root.relative_to(VAULT_ROOT)
        except ValueError:
            label = root
        print(f"\nScanning {label} ...")
        p, s = scan_root(
            root, exclude_names, derive_path_tags,
            expected_stems, seen_stems,
            seen_attachment_files, seen_attachment_dirs,
        )
        total_processed += p
        total_skipped += s

    # Only prune stale .qmd files when the full vault scan ran.  Without the
    # vault, expected_stems covers only _notes/; pruning would wrongly remove
    # vault-wide notes committed locally that should remain deployed.
    if vault_present:
        removed = prune_stale(expected_stems)
    else:
        removed = 0

    print(
        f"\n--- Done. Copied {total_processed} note(s)"
        f", skipped {total_skipped} collision(s)"
        f", pruned {removed} stale file(s). ---"
    )


if __name__ == "__main__":
    main()
