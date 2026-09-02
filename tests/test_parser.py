import textwrap
from pathlib import Path

from src.frontmatter_handler.parser import load_frontmatter


class TestLoadFrontmatter:
    def test_good_frontmatter(self, sample_files):
        f = sample_files["good"]
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is True
        assert front["title"] == "Good frontmatter"
        assert front["tags"] == ["python", "pytest"]
        assert front["published"] is True
        assert content == "This is the post content."

    def test_no_frontmatter(self, sample_files):
        f = sample_files["none"]
        front, content, has_fm = load_frontmatter(f)
        assert front == {}
        assert has_fm is False
        assert "just a markdown file\nwithout ---" in content

    def test_bad_yaml_syntax(self, sample_files):
        f = sample_files["bad1"]
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is False
        assert front == {}
        assert "Content." in content

    def test_missing_closing_delimiter(self, sample_files):
        f = sample_files["bad2"]
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is False
        assert front == {}
        assert "Its open?" in content

    def test_list_only_frontmatter(self, sample_files):
        f = sample_files["bad3"]
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is False
        assert front == {}
        assert "Content." in content

    def test_no_content_after_frontmatter(self, sample_files):
        f = sample_files["nocontent"]
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is True
        assert content == []

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.md"
        f.write_text("")
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is False
        assert front == {}

    def test_only_delimiters_no_newline_between(self, tmp_path):
        """---\\n---\\n has no content between delimiters; regex can't match,
        so the parser falls back to treating it as raw content."""
        f = tmp_path / "delims.md"
        f.write_text("---\n---\n")
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is False
        assert front == {}

    def test_empty_frontmatter_block(self, tmp_path):
        """---\\n\\n---\\n has an empty line between delimiters; YAML parses as None."""
        f = tmp_path / "empty_fm.md"
        f.write_text("---\n\n---\nContent.")
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is True
        assert front is None

    def test_special_characters_in_values(self, tmp_path):
        f = tmp_path / "special.md"
        f.write_text(textwrap.dedent("""\
            ---
            title: "Café & naïve — résumé"
            path: "a/b/c"
            ---
            Content here.
        """).strip())
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is True
        assert "Café" in front["title"]
        assert content == "Content here."

    def test_multiline_string_value(self, tmp_path):
        f = tmp_path / "multi.md"
        f.write_text(textwrap.dedent("""\
            ---
            title: |
              Line one
              Line two
            ---
            Body.
        """).strip())
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is True
        assert "Line one" in front["title"]

    def test_numeric_values(self, tmp_path):
        f = tmp_path / "nums.md"
        f.write_text(textwrap.dedent("""\
            ---
            count: 42
            ratio: 3.14
            ---
            Body.
        """).strip())
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is True
        assert front["count"] == 42
        assert front["ratio"] == 3.14

    def test_boolean_values(self, tmp_path):
        f = tmp_path / "bools.md"
        f.write_text(textwrap.dedent("""\
            ---
            draft: true
            published: false
            ---
            Body.
        """).strip())
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is True
        assert front["draft"] is True
        assert front["published"] is False

    def test_null_value(self, tmp_path):
        f = tmp_path / "nullval.md"
        f.write_text(textwrap.dedent("""\
            ---
            key: null
            ---
            Body.
        """).strip())
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is True
        assert front["key"] is None

    def test_deeply_nested_yaml(self, tmp_path):
        f = tmp_path / "nested.md"
        f.write_text(textwrap.dedent("""\
            ---
            meta:
              author:
                name: Alice
            tags: [a, b]
            ---
            Body.
        """).strip())
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is True
        assert front["meta"]["author"]["name"] == "Alice"
        assert front["tags"] == ["a", "b"]

    def test_whitespace_before_delimiter(self, tmp_path):
        f = tmp_path / "ws.md"
        f.write_text("  \n---\ntitle: t\n---\ncontent")
        front, content, has_fm = load_frontmatter(f)
        assert has_fm is True
        assert front["title"] == "t"
