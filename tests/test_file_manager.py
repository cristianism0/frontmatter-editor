import pytest
import textwrap
from src.file_handle.file_manager import  collect_dirs_and_files, file_reconstruct
from src.file_handle.file_manager import  metadata_remover, metadata_add, metadata_changer, load_frontmatter
from tests.test_parser import files_samples

def test_collect_dirs_and_files(tmp_path):
    d = tmp_path / "docs"
    excluded = tmp_path / "excluded"

    d.mkdir()
    excluded.mkdir()

    ex_file = excluded / 'ex_file.md'
    file1 = d / 'file1.md'
    file2 = d / 'file2.md'


    ex_file.write_text("---\ntest: excluded\n---\n")
    file1.write_text("---\ntest: num 1\n---\n")
    file2.write_text("---\ntest: num 2\n---\n")

    dirs, files = collect_dirs_and_files(path = tmp_path, exclude_dirs = [excluded], backup_path = tmp_path / "backup")

    assert d in dirs
    assert file1 in files
    assert file2 in files
    assert excluded not in files
def test_file_reconstruct(tmp_path):
    """Test reconstruct diferent paths."""
    good, none, bad1, bad2, bad3, nocontent = files_samples(tmp_path)

    goodfront, goodcontent, has_frontmatter_good = load_frontmatter(good)
    nonefront, nonecontent, has_frontmatter_none = load_frontmatter(none)
    bad1front, bad1content, has_frontmatter_bad1 = load_frontmatter(bad1)
    nocontentfront, nocontentcontent, has_frontmatter_nococent = load_frontmatter(nocontent)

    reconstructed_good = tmp_path / "reconstructed_good.md"
    reconstructed_none = tmp_path / "reconstructed_none.md"
    reconstructed_bad1 = tmp_path / "reconstructed_bad1.md"
    reconstructed_bad2 = tmp_path / "reconstructed_bad2.md"
    reconstructed_bad3 = tmp_path / "reconstructed_bad3.md"
    reconstructed_nocontent = tmp_path / "reconstructed_nocontent.md"

    # good
    file_reconstruct(
        file=reconstructed_good,
        header=goodfront,
        body=goodcontent,
        frontmatter=True
    )

    expected_good_content = textwrap.dedent(f"""
        ---
        title: Good frontmatter
        date: 2023-10-27
        tags: ['python', 'pytest']
        published: True
        ---
        This is the post content.
    """).strip()

    assert reconstructed_good.read_text().strip() == expected_good_content

    # None
    file_reconstruct(
        file=reconstructed_none,
        header=nonefront,
        body=nonecontent,
        frontmatter=False
    )
    assert reconstructed_none.read_text().strip() == nonecontent.strip()

    # Nocontent
    file_reconstruct(
        file=reconstructed_nocontent,
        header=nocontentfront,
        body=nocontentcontent,
        frontmatter=True
    )
    expected_nocontent_content = textwrap.dedent(f"""
        ---
        title: no content
        date: 2023-10-27
        tags: ['python', 'pytest']
        published: True
        ---
        
    """).strip()

    assert reconstructed_nocontent.read_text().strip() == expected_nocontent_content

    # Bad -> all the other files will receive its content on body, so, just this is enought
    if bad1front == {}:
        file_reconstruct(
            file=reconstructed_bad1,
            header=bad1front,
            body=bad1content,
            frontmatter=True
        )
        
        assert bad1front == {}
        assert bad1content in reconstructed_bad1.read_text()
        assert "item 2 with bad indentation" in reconstructed_bad1.read_text()
        assert "Content." in reconstructed_bad1.read_text()


