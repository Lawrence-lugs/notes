# Web-accessible Personal Notes

When I moved from Notion to Obsidian, it became difficult to share important sections of notes to other people.
This repository fixes that (it's a subfolder of the Obsidian space).
Additionally, here is where my revealJS slides are deployed (because there's no other way to have those accessible outside localhost).

## Devcontainer and Docker

The devcontainer and dockerfile contains a quarto + latex + micromamba installation.
See ghcr.io/lawrence-lugs/quartolatex

## Selective Per-File GFM Conversion

If you want conversion only for specific notes (instead of project-wide pre-render), use the Lua filter at [scripts/gfm_to_quarto_filter.lua](scripts/gfm_to_quarto_filter.lua).

Add this to the target note front matter:

```yaml
---
filters:
	- scripts/gfm_to_quarto_filter.lua
---
```

For notes under a subfolder, adjust the relative path, for example:

```yaml
---
filters:
	- ../scripts/gfm_to_quarto_filter.lua
---
```

Current filter behavior:

1. Converts Obsidian/GFM callouts like `> [!NOTE] Title` blockquotes into Quarto callout divs.
2. Normalizes unsupported callout types to Quarto-safe types (`note`, `tip`, `important`, `warning`, `caution`).
3. Handles aliases: `quote -> note`, `question -> tip`, `example -> note`.
