function Div(el)
  if el.classes:includes('auto-fragment-children') then
    
    -- 1. Check for a custom style attribute
    -- Default to 'fade-in-then-semi-out' if not provided
    local anim_style = el.attributes['style'] or 'fade-in'
    
    -- 2. Remove the 'style' attribute from the parent 
    -- (so it doesn't render as invalid CSS in the final HTML)
    el.attributes['style'] = nil

    local new_content = {}
    
    -- 3. Iterate and wrap children
    for _, block in ipairs(el.content) do
      
      -- If child is a Div (grouped content), just append classes
      if block.t == 'Div' then
        block.classes:insert('fragment')
        block.classes:insert(anim_style)
        table.insert(new_content, block)
      
      -- Otherwise wrap the block in a new Div
      else
        local wrapper = pandoc.Div(
          {block}, 
          pandoc.Attr("", {"fragment", anim_style})
        )
        table.insert(new_content, wrapper)
      end
    end
    
    el.content = new_content
    return el
  end
end