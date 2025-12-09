from src.frontmatter_handler.parser import load_frontmatter

def test_load_frontmatter(tmp_path):
    import textwrap
    """
    Test the load frontmatter in different scenarios
    """
    good = tmp_path / "good.md"
    good.write_text(textwrap.dedent("""
        ---
        title: "Good frontmatter"
        date: 2023-10-27
        tags: [python, pytest]
        published: true
        ---
        This is the post content.
    """).strip(), encoding="utf-8")

    none = tmp_path / "none.md"
    none.write_text(textwrap.dedent("""
        just a markdown file
        without ---
    """).strip(), encoding="utf-8")

    bad1 = tmp_path / "bad_syntax.md"
    bad1.write_text(textwrap.dedent("""
        ---
        title: "Indentation Error"
        description:
          - item 1
         - item 2 with bad indentation
        ---
        Content.
    """).strip(), encoding="utf-8")

    bad2 = tmp_path / "missing_delimiter.md"
    bad2.write_text(textwrap.dedent("""
        ---
        title: "Open frontmatter"
        author: me
        
        Its open?
    """).strip(), encoding="utf-8")

    bad3 = tmp_path / "list_root.md"
    bad3.write_text(textwrap.dedent("""
        ---
        - A list
        - No keys
        - Only items
        ---
        Content.
    """).strip(), encoding="utf-8")

    #### ASSERTS
    # good
    front, content, has_frontmatter_good = load_frontmatter(good)
    assert has_frontmatter_good == True
    assert front["title"] == "Good frontmatter"
    assert front["tags"] == ['python', 'pytest']
    assert front["published"] == True
    assert content == "This is the post content."

    # none
    front, content, has_frontmatter_none = load_frontmatter(none)
    assert front == {}
    assert has_frontmatter_none == False
    assert "just a markdown file\nwithout ---" in content 

    #bad1
    front, content, has_frontmatter_bad1 = load_frontmatter(bad1)
    assert has_frontmatter_bad1 == False
    assert front == {}    
    assert r"""---
title: "Indentation Error"
description:
  - item 1
 - item 2 with bad indentation
---
Content.""" == content
    
    #bad 2
    front, content, has_frontmatter_bad2 = load_frontmatter(bad2)
    assert has_frontmatter_bad2 == False
    assert front == {}    
    assert r"""---
title: "Open frontmatter"
author: me

Its open?""" == content
    
    #bad 3
    front, content, has_frontmatter_bad3 = load_frontmatter(bad3)
    assert has_frontmatter_bad3 == False
    assert front == {}    
    assert r"""---
- A list
- No keys
- Only items
---
Content.""" == content