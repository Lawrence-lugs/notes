local function apply_auto_fragment_children(el)
  if not el.classes:includes('auto-fragment-children') then
    return nil
  end

  -- style= is used as animation class, not CSS.
  local anim_style = el.attributes['style'] or 'fade-in-then-semi-out'
  el.attributes['style'] = nil

  local new_content = pandoc.List()

  for _, block in ipairs(el.content) do
    if block.t == 'Div' then
      block.classes:insert('fragment')
      block.classes:insert(anim_style)
      new_content:insert(block)
    else
      local wrapper = pandoc.Div(
        { block },
        pandoc.Attr('', { 'fragment', anim_style })
      )
      new_content:insert(wrapper)
    end
  end

  el.content = new_content
  return el
end

function Div(el)
  -- Slide-level shorthand: fragment every body block on the slide.
  if el.classes:includes('auto-fragment-slide') then
    local anim_style = el.attributes['style'] or 'fade-in-then-semi-out'
    el.attributes['style'] = nil

    local new_content = pandoc.List()
    local body_start = 1

    -- Keep the slide title (if present) out of the auto-fragment body wrapper.
    if #el.content > 0 and el.content[1].t == 'Header' then
      new_content:insert(el.content[1])
      body_start = 2
    end

    if body_start <= #el.content then
      local body_blocks = pandoc.List()
      for i = body_start, #el.content do
        body_blocks:insert(el.content[i])
      end

      local body_wrapper = pandoc.Div(
        body_blocks,
        pandoc.Attr('', { 'auto-fragment-children' }, { style = anim_style })
      )

      new_content:insert(apply_auto_fragment_children(body_wrapper))
    end

    el.content = new_content
    return el
  end

  return apply_auto_fragment_children(el)
end

function Pandoc(doc)
  -- Support heading syntax: ## Title {.auto-fragment-slide}
  local blocks = doc.blocks
  local out = pandoc.List()
  local i = 1

  while i <= #blocks do
    local block = blocks[i]

    if block.t == 'Header' and block.classes:includes('auto-fragment-slide') then
      local anim_style = block.attributes['style'] or 'fade-in-then-semi-out'
      block.attributes['style'] = nil
      out:insert(block)

      i = i + 1
      local slide_body = pandoc.List()

      while i <= #blocks do
        local next_block = blocks[i]
        if next_block.t == 'Header' and next_block.level <= block.level then
          break
        end
        slide_body:insert(next_block)
        i = i + 1
      end

      if #slide_body > 0 then
        local body_wrapper = pandoc.Div(
          slide_body,
          pandoc.Attr('', { 'auto-fragment-children' }, { style = anim_style })
        )
        out:insert(apply_auto_fragment_children(body_wrapper))
      end
    else
      out:insert(block)
      i = i + 1
    end
  end

  doc.blocks = out
  return doc
end