import pytest
from unittest.mock import MagicMock
import textwrap
from src.file_handle.file_manager import  collect_dirs_and_files, file_reconstruct
from src.file_handle.file_manager import  metadata_remover, metadata_set_update, load_frontmatter
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

@pytest.fixture
def files_list(tmp_path):
    """Create and return path for md files"""
    f1 = tmp_path / "file1.md"
    f2 = tmp_path / "file2.md"
    f3 = tmp_path / "file3.md"
    f1.write_text("content") 
    f2.write_text("content")
    f3.write_text("content")
    return [f1, f2, f3]

FRONTMATTER_WITH_KEY = ({"title": "Old Title", "tag": "test"}, ["Body Line"], True)
FRONTMATTER_WITHOUT_KEY = ({"title": "Old Title"}, ["Body Line"], True)
NO_FRONTMATTER = ({}, ["All content"], False)

def test_metadata_remover_successful_dry_run(mocker, files_list):
    """Test with dry-run"""
    
    mocker.patch("src.file_handle.file_manager.load_frontmatter", return_value=FRONTMATTER_WITH_KEY)
    mock_reconstruct = mocker.patch("src.file_handle.file_manager.file_reconstruct")
    
    key_to_delete = "tag"
    file_path = files_list[0].as_posix()
    
    keys, prev, after, status, action = metadata_remover(key_to_delete, files_list[:1], dry_run=True)
    
    assert prev[file_path] == "test"
    assert after[file_path] == "removed"
    assert "has frontmatter" in status[file_path]
    mock_reconstruct.assert_not_called()

def test_metadata_remover_key_not_found(mocker, files_list):
    """Test if key is not in the file"""
    mocker.patch("src.file_handle.file_manager.load_frontmatter", return_value=FRONTMATTER_WITHOUT_KEY)
    mock_reconstruct = mocker.patch("src.file_handle.file_manager.file_reconstruct")
    
    key_to_delete = "nonexistent_key"
    file_path = files_list[0].as_posix()
    
    keys, prev, after, status, action= metadata_remover(key_to_delete, files_list[:1], dry_run=True)

    assert prev[file_path] is None
    assert after[file_path] == "failed"
    mock_reconstruct.assert_not_called()

def test_metadata_remover_no_frontmatter(mocker, files_list):
    """Test the pop fail"""
    mocker.patch("src.file_handle.file_manager.load_frontmatter", return_value=NO_FRONTMATTER)
    mocker.patch("src.file_handle.file_manager.file_reconstruct")
    
    key_to_delete = "any_key"
    file_path = files_list[0].as_posix()

    keys, prev, after, status, action = metadata_remover(key_to_delete, files_list[:1], dry_run=True)

    assert prev[file_path] is None
    assert after[file_path] == "failed"
    assert "doesn't have frontmatter" in status[file_path]
    
def test_metadata_set_update_successful_change(mocker, files_list):
    """Test the change and the log"""
    mock_load = mocker.patch("src.file_handle.file_manager.load_frontmatter", return_value=FRONTMATTER_WITH_KEY)
    mock_reconstruct = mocker.patch("src.file_handle.file_manager.file_reconstruct")
    
    key_to_change = "title"
    new_content = "New Title"
    file_path = files_list[0].as_posix()
    
    keys, prev, after, status, action = metadata_set_update(key_to_change, new_content, files_list[:1], dry_run=False)

    assert prev[file_path] == "Old Title"
    assert after[file_path] == "New Title"
    assert "has frontmatter" in status[file_path]
    
    mock_reconstruct.assert_called_once()

def test_metadata_set_update_add_new_key(mocker, files_list):
    """Test changing a new key, it will create if its not exist"""
    mocker.patch("src.file_handle.file_manager.load_frontmatter", return_value=FRONTMATTER_WITHOUT_KEY)
    mock_reconstruct = mocker.patch("src.file_handle.file_manager.file_reconstruct")
    
    key_to_add = "date"
    new_content = "2025-12-10"
    file_path = files_list[0].as_posix()
    
    keys, prev, after, status, action = metadata_set_update(key_to_add, new_content, files_list[:1], dry_run=True)

    assert prev[file_path] is None
    assert after[file_path] == new_content
    
    mock_reconstruct.assert_not_called()
