import textwrap
import pytest
from pathlib import Path


@pytest.fixture
def files_list(tmp_path):
    """Create and return paths for three stub .md files."""
    f1 = tmp_path / "file1.md"
    f2 = tmp_path / "file2.md"
    f3 = tmp_path / "file3.md"
    f1.write_text("content")
    f2.write_text("content")
    f3.write_text("content")
    return [f1, f2, f3]


@pytest.fixture
def sample_files(tmp_path):
    """Create the six standard sample files used across parser and file_manager tests.

    Returns a dict with keys: good, none, bad1, bad2, bad3, nocontent
    """
    good = tmp_path / "good.md"
    good.write_text(textwrap.dedent("""\
        ---
        title: "Good frontmatter"
        date: 2023-10-27
        tags: [python, pytest]
        published: true
        ---
        This is the post content.
    """).strip(), encoding="utf-8")

    none = tmp_path / "none.md"
    none.write_text(textwrap.dedent("""\
        just a markdown file
        without ---
    """).strip(), encoding="utf-8")

    bad1 = tmp_path / "bad_syntax.md"
    bad1.write_text(textwrap.dedent("""\
        ---
        title: "Indentation Error"
        description:
          - item 1
         - item 2 with bad indentation
        ---
        Content.
    """).strip(), encoding="utf-8")

    bad2 = tmp_path / "missing_delimiter.md"
    bad2.write_text(textwrap.dedent("""\
        ---
        title: "Open frontmatter"
        author: me

        Its open?
    """).strip(), encoding="utf-8")

    bad3 = tmp_path / "list_root.md"
    bad3.write_text(textwrap.dedent("""\
        ---
        - A list
        - No keys
        - Only items
        ---
        Content.
    """).strip(), encoding="utf-8")

    nocontent = tmp_path / "nocontent.md"
    nocontent.write_text(textwrap.dedent("""\
        ---
        title: "no content"
        date: 2023-10-27
        tags: [python, pytest]
        published: true
        ---
    """).strip(), encoding="utf-8")

    return {
        "good": good,
        "none": none,
        "bad1": bad1,
        "bad2": bad2,
        "bad3": bad3,
        "nocontent": nocontent,
    }


FRONTMATTER_WITH_KEY = ({"title": "Old Title", "tag": "test"}, ["Body Line"], True)
FRONTMATTER_WITHOUT_KEY = ({"title": "Old Title"}, ["Body Line"], True)
NO_FRONTMATTER = ({}, ["All content"], False)
FRONTMATTER_MULTI_KEY = (
    {"title": "T", "author": "A", "date": "2024-01-01"},
    ["Body"],
    True,
)
