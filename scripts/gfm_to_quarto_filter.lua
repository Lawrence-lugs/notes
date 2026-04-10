-- Quarto/Pandoc Lua filter for selective per-document GFM -> Quarto fixes.
-- Enable on a specific note with front matter:
-- filters:
--   - ../scripts/gfm_to_quarto_filter.lua

local SUPPORTED_CALLOUT_TYPES = {
  note = true,
  tip = true,
  important = true,
  warning = true,
  caution = true,
}

local CALLOUT_CONVERSION_TABLE = {
  quote = "note",
  question = "tip",
  example = "note",
}

local DEFAULT_TITLES = {
  note = "Note",
  tip = "Tip",
  important = "Important",
  warning = "Warning",
  caution = "Caution",
}

local MERMAID_PRESENT = false

local function has_class(el, class_name)
  for _, class in ipairs(el.classes or {}) do
    if class == class_name then
      return true
    end
  end
  return false
end

local function html_escape(text)
  return text
    :gsub("&", "&amp;")
    :gsub("<", "&lt;")
    :gsub(">", "&gt;")
end

local function is_html_output()
  return FORMAT:match("html") ~= nil
end

local function is_markdown_like_output()
  -- Spacing normalization only makes sense for markdown-like writers.
  return FORMAT:match("markdown")
    or FORMAT:match("gfm")
    or FORMAT:match("commonmark")
    or FORMAT:match("quarto")
end

local function is_list_block(block)
  return block.t == "BulletList"
    or block.t == "OrderedList"
    or block.t == "DefinitionList"
end

local function is_spacing_marker(block)
  return block.t == "RawBlock"
    and block.format == "markdown"
    and block.text == ""
end

local function needs_spacing_before(block)
  return block.t == "Header" or is_list_block(block)
end

local function trim(s)
  return (s:gsub("^%s+", ""):gsub("%s+$", ""))
end

local function normalize_callout_type(raw_type)
  local t = string.lower(raw_type or "")
  if SUPPORTED_CALLOUT_TYPES[t] then
    return t
  end
  return CALLOUT_CONVERSION_TABLE[t] or "note"
end

local function extract_callout_marker(inlines)
  if #inlines == 0 then
    return nil
  end

  local first = inlines[1]
  if first.t ~= "Str" then
    return nil
  end

  local raw_type = first.text:match("^%[!([%w%-]+)%]$")
  if not raw_type then
    return nil
  end

  local tail_start = 2
  if inlines[2] and inlines[2].t == "Space" then
    tail_start = 3
  end

  local title_inlines = {}
  local body_inlines = {}
  local in_title = true

  for i = tail_start, #inlines do
    local el = inlines[i]
    if in_title and el.t == "SoftBreak" then
      in_title = false
    elseif in_title then
      title_inlines[#title_inlines + 1] = el
    else
      body_inlines[#body_inlines + 1] = el
    end
  end

  local title = trim(pandoc.utils.stringify(title_inlines))

  return {
    callout_type = normalize_callout_type(raw_type),
    title = title,
    body_inlines = body_inlines,
  }
end

function BlockQuote(el)
  if #el.content == 0 then
    return nil
  end

  local first_block = el.content[1]
  if first_block.t ~= "Para" and first_block.t ~= "Plain" then
    return nil
  end

  local marker = extract_callout_marker(first_block.content)
  if not marker then
    return nil
  end

  local blocks = {}

  if #marker.body_inlines > 0 then
    if first_block.t == "Para" then
      blocks[#blocks + 1] = pandoc.Para(marker.body_inlines)
    else
      blocks[#blocks + 1] = pandoc.Plain(marker.body_inlines)
    end
  end

  for i = 2, #el.content do
    blocks[#blocks + 1] = el.content[i]
  end

  local title_text = marker.title
  if title_text == "" then
    title_text = DEFAULT_TITLES[marker.callout_type] or "Note"
  end

  local title_para = pandoc.Para({pandoc.Strong({pandoc.Str(title_text)})})

  local callout_title = pandoc.Div(
    {
      pandoc.Div({pandoc.RawBlock("html", "<i class=\"callout-icon\"></i>")}, pandoc.Attr("", {"callout-icon-container"})),
      title_para,
    },
    pandoc.Attr("", {"callout-title"})
  )

  local callout_content = pandoc.Div(blocks, pandoc.Attr("", {"callout-content"}))
  local callout_body = pandoc.Div({callout_title, callout_content}, pandoc.Attr("", {"callout-body"}))

  local callout = pandoc.Div(
    {callout_body},
    pandoc.Attr("", {"callout", "callout-" .. marker.callout_type, "callout-titled", "callout-style-default"})
  )

  if marker.title ~= "" then
    return pandoc.Div({callout}, pandoc.Attr("", {}, {title = marker.title}))
  end

  return callout
end

function CodeBlock(el)
  if not has_class(el, "mermaid") then
    return nil
  end

  MERMAID_PRESENT = true

  -- Quarto decides executable cells before Lua filters run, so converting
  -- ```mermaid to ```{mermaid} cannot be done here. For HTML output we
  -- render Mermaid directly to avoid ending up with a plain code block.
  if is_html_output() then
    return pandoc.RawBlock("html", "<pre class=\"mermaid\">\n" .. html_escape(el.text) .. "\n</pre>")
  end

  -- Keep class-normalized blocks for non-HTML targets.
  local attrs = pandoc.Attr(el.identifier, {"mermaid"}, el.attributes)
  return pandoc.CodeBlock(el.text, attrs)
end

local function append_header_include(meta, raw_html)
  local existing = meta["header-includes"]
  local block = pandoc.RawBlock("html", raw_html)

  if existing == nil then
    meta["header-includes"] = pandoc.MetaBlocks({block})
    return
  end

  if existing.t == "MetaBlocks" then
    local blocks = existing
    blocks[#blocks + 1] = block
    meta["header-includes"] = pandoc.MetaBlocks(blocks)
    return
  end

  if existing.t == "MetaInlines" then
    local blocks = {pandoc.Plain(existing), block}
    meta["header-includes"] = pandoc.MetaBlocks(blocks)
    return
  end

  meta["header-includes"] = pandoc.MetaBlocks({block})
end

function Pandoc(doc)
  if is_html_output() and MERMAID_PRESENT then
    append_header_include(doc.meta, [[<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({ startOnLoad: true });</script>]])
  end

  if not is_markdown_like_output() then
    return doc
  end

  local normalized = {}
  for i, block in ipairs(doc.blocks) do
    if i > 1 and needs_spacing_before(block) then
      local prev = normalized[#normalized]
      if prev
        and prev.t ~= "Header"
        and not is_list_block(prev)
        and not is_spacing_marker(prev)
      then
        normalized[#normalized + 1] = pandoc.RawBlock("markdown", "")
      end
    end
    normalized[#normalized + 1] = block
  end

  doc.blocks = normalized
  return doc
end
