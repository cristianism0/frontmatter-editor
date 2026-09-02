from src.file_handle.file_manager import (
    collect_dirs_and_files,
    file_reconstruct,
    metadata_remover,
    metadata_set_update,
)
from tests.conftest import (
    FRONTMATTER_WITH_KEY,
    FRONTMATTER_WITHOUT_KEY,
    NO_FRONTMATTER,
)

# ---------------------------------------------------------------------------
# collect_dirs_and_files
# ---------------------------------------------------------------------------
class TestCollectDirsAndFiles:
    def test_collects_subdirectory_files(self, tmp_path):
        d = tmp_path / "docs"
        d.mkdir()
        f1 = d / "file1.md"
        f2 = d / "file2.md"
        f1.write_text("---\ntest: 1\n---\n")
        f2.write_text("---\ntest: 2\n---\n")

        dirs, files = collect_dirs_and_files(
            path=tmp_path, exclude_dirs=[], backup_path=tmp_path / "backup"
        )
        assert f1 in files
        assert f2 in files

    def test_collects_root_level_files(self, tmp_path):
        root_file = tmp_path / "root.md"
        root_file.write_text("---\ntitle: root\n---\n")
        sub = tmp_path / "sub"
        sub.mkdir()
        sub_file = sub / "sub.md"
        sub_file.write_text("---\ntitle: sub\n---\n")

        dirs, files = collect_dirs_and_files(
            path=tmp_path, exclude_dirs=[], backup_path=tmp_path / "backup"
        )
        assert root_file in files
        assert sub_file in files

    def test_excludes_non_md_files(self, tmp_path):
        d = tmp_path / "docs"
        d.mkdir()
        txt = d / "file.txt"
        py = d / "script.py"
        md = d / "note.md"
        for f in (txt, py, md):
            f.write_text("content")

        dirs, files = collect_dirs_and_files(
            path=tmp_path, exclude_dirs=[], backup_path=tmp_path / "backup"
        )
        assert md in files
        assert txt not in files
        assert py not in files

    def test_excludes_specified_directories(self, tmp_path):
        excl = tmp_path / "excluded"
        incl = tmp_path / "included"
        excl.mkdir()
        incl.mkdir()
        (excl / "e.md").write_text("---\ntitle: e\n---\n")
        (incl / "i.md").write_text("---\ntitle: i\n---\n")

        dirs, files = collect_dirs_and_files(
            path=tmp_path, exclude_dirs=["excluded"], backup_path=tmp_path / "backup"
        )
        assert (excl / "e.md") not in files
        assert (incl / "i.md") in files

    def test_empty_directory(self, tmp_path):
        dirs, files = collect_dirs_and_files(
            path=tmp_path, exclude_dirs=[], backup_path=tmp_path / "backup"
        )
        assert files == []

    def test_excludes_backup_directory(self, tmp_path):
        backup = tmp_path / "backup"
        backup.mkdir()
        (backup / "old.md").write_text("content")

        dirs, files = collect_dirs_and_files(
            path=tmp_path, exclude_dirs=[], backup_path=backup
        )
        assert not any(f.name == "old.md" for f in files)

    def test_excludes_hidden_directories(self, tmp_path):
        hidden = tmp_path / ".hidden"
        hidden.mkdir()
        (hidden / "secret.md").write_text("content")

        dirs, files = collect_dirs_and_files(
            path=tmp_path, exclude_dirs=[], backup_path=tmp_path / "backup"
        )
        assert not any(f.name == "secret.md" for f in files)

    def test_excludes_pycache(self, tmp_path):
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (cache / "cached.md").write_text("content")

        dirs, files = collect_dirs_and_files(
            path=tmp_path, exclude_dirs=["__pycache__"], backup_path=tmp_path / "backup"
        )
        assert not any(f.name == "cached.md" for f in files)


# ---------------------------------------------------------------------------
# file_reconstruct
# ---------------------------------------------------------------------------
class TestFileReconstruct:
    def test_reconstructs_with_frontmatter(self, tmp_path):
        out = tmp_path / "out.md"
        file_reconstruct(
            file=out,
            header={"title": "T", "date": "2024-01-01"},
            body=["Body content"],
            frontmatter=True,
        )
        text = out.read_text()
        assert text.startswith("---\n")
        assert "title: T\n" in text
        assert "date: 2024-01-01\n" in text
        assert text.endswith("---\nBody content")

    def test_reconstructs_without_frontmatter(self, tmp_path):
        out = tmp_path / "out.md"
        file_reconstruct(
            file=out,
            header={},
            body=["Just content"],
            frontmatter=False,
        )
        text = out.read_text()
        assert "---" not in text
        assert "Just content" in text

    def test_empty_header_with_frontmatter_flag(self, tmp_path):
        out = tmp_path / "out.md"
        file_reconstruct(
            file=out,
            header={},
            body=["Body"],
            frontmatter=True,
        )
        text = out.read_text()
        assert text.startswith("---\n---\n")
        assert "Body" in text

    def test_body_as_list(self, tmp_path):
        out = tmp_path / "out.md"
        file_reconstruct(
            file=out,
            header={"k": "v"},
            body=["line1\n", "line2\n"],
            frontmatter=True,
        )
        text = out.read_text()
        assert "line1\n" in text
        assert "line2\n" in text

    def test_body_as_string(self, tmp_path):
        out = tmp_path / "out.md"
        file_reconstruct(
            file=out,
            header={"k": "v"},
            body="single line body",
            frontmatter=True,
        )
        text = out.read_text()
        assert "single line body" in text

    def test_unicode_content(self, tmp_path):
        out = tmp_path / "out.md"
        file_reconstruct(
            file=out,
            header={"title": "Café"},
            body=["Contenu français"],
            frontmatter=True,
        )
        text = out.read_text()
        assert "Café" in text
        assert "Contenu français" in text


# ---------------------------------------------------------------------------
# metadata_remover
# ---------------------------------------------------------------------------
class TestMetadataRemover:
    def test_dry_run_does_not_write(self, mocker, files_list):
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=FRONTMATTER_WITH_KEY,
        )
        mock_reconstruct = mocker.patch("src.file_handle.file_manager.file_reconstruct")
        fp = files_list[0].as_posix()

        keys, prev, after, status, action = metadata_remover(
            "tag", files_list[:1], dry_run=True
        )

        assert prev[fp] == "test"
        assert after[fp] == "removed"
        mock_reconstruct.assert_not_called()

    def test_non_dry_run_writes_file(self, mocker, tmp_path):
        f = tmp_path / "real.md"
        f.write_text("---\ntitle: T\ntag: old\n---\nBody\n")
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=({"title": "T", "tag": "old"}, ["Body\n"], True),
        )
        mock_reconstruct = mocker.patch("src.file_handle.file_manager.file_reconstruct")

        metadata_remover("tag", [f], dry_run=False)
        mock_reconstruct.assert_called_once()

    def test_key_not_found(self, mocker, files_list):
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=FRONTMATTER_WITHOUT_KEY,
        )
        fp = files_list[0].as_posix()

        keys, prev, after, status, action = metadata_remover(
            "nonexistent", files_list[:1], dry_run=True
        )

        assert prev[fp] is None
        assert after[fp] == "failed"

    def test_no_frontmatter(self, mocker, files_list):
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=NO_FRONTMATTER,
        )
        fp = files_list[0].as_posix()

        keys, prev, after, status, action = metadata_remover(
            "any_key", files_list[:1], dry_run=True
        )

        assert "doesn't have frontmatter" in status[fp]
        assert after[fp] == "failed"

    def test_multiple_files(self, mocker):
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            f1 = Path(td) / "a.md"
            f2 = Path(td) / "b.md"
            f1.touch()
            f2.touch()
            mocker.patch(
                "src.file_handle.file_manager.load_frontmatter",
                return_value=({"key": "val"}, ["body"], True),
            )
            mock_reconstruct = mocker.patch("src.file_handle.file_manager.file_reconstruct")

            keys, prev, after, status, action = metadata_remover(
                "key", [f1, f2], dry_run=True
            )

            assert len(prev) == 2
            assert len(after) == 2
            mock_reconstruct.assert_not_called()

    def test_status_reports_has_frontmatter(self, mocker, files_list):
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=FRONTMATTER_WITH_KEY,
        )
        fp = files_list[0].as_posix()

        _, _, _, status, _ = metadata_remover("tag", files_list[:1], dry_run=True)
        assert "has frontmatter" in status[fp]

    def test_action_is_remove(self, mocker, files_list):
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=FRONTMATTER_WITH_KEY,
        )
        fp = files_list[0].as_posix()

        _, _, _, _, action = metadata_remover("tag", files_list[:1], dry_run=True)
        assert action[fp] == "remove"

    def test_keys_dict_populated(self, mocker, files_list):
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=FRONTMATTER_WITH_KEY,
        )
        fp = files_list[0].as_posix()

        keys_dict, _, _, _, _ = metadata_remover("tag", files_list[:1], dry_run=True)
        assert keys_dict[fp] == "tag"


# ---------------------------------------------------------------------------
# metadata_set_update
# ---------------------------------------------------------------------------
class TestMetadataSetUpdate:
    def test_dry_run_change_existing_key(self, mocker, files_list):
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=FRONTMATTER_WITH_KEY,
        )
        mock_reconstruct = mocker.patch("src.file_handle.file_manager.file_reconstruct")
        fp = files_list[0].as_posix()

        keys, prev, after, status, action = metadata_set_update(
            "title", "New Title", files_list[:1], dry_run=True
        )

        assert prev[fp] == "Old Title"
        assert after[fp] == "New Title"
        assert action[fp] == "change"
        mock_reconstruct.assert_not_called()

    def test_dry_run_add_new_key(self, mocker, files_list):
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=FRONTMATTER_WITHOUT_KEY,
        )
        mock_reconstruct = mocker.patch("src.file_handle.file_manager.file_reconstruct")
        fp = files_list[0].as_posix()

        keys, prev, after, status, action = metadata_set_update(
            "date", "2025-12-10", files_list[:1], dry_run=True
        )

        assert prev[fp] is None
        assert after[fp] == "2025-12-10"
        assert action[fp] == "add"
        mock_reconstruct.assert_not_called()

    def test_non_dry_run_writes_file(self, mocker, tmp_path):
        f = tmp_path / "real.md"
        f.write_text("---\ntitle: Old\n---\nBody\n")
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=({"title": "Old"}, ["Body\n"], True),
        )
        mock_reconstruct = mocker.patch("src.file_handle.file_manager.file_reconstruct")

        metadata_set_update("title", "New", [f], dry_run=False)
        mock_reconstruct.assert_called_once()

    def test_no_frontmatter_adds_key(self, mocker, files_list):
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=NO_FRONTMATTER,
        )
        fp = files_list[0].as_posix()

        keys, prev, after, status, action = metadata_set_update(
            "new_key", "value", files_list[:1], dry_run=True
        )

        assert "doesn't have frontmatter" in status[fp]
        assert action[fp] == "add"
        assert after[fp] == "value"

    def test_status_reports_has_frontmatter(self, mocker, files_list):
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=FRONTMATTER_WITH_KEY,
        )
        fp = files_list[0].as_posix()

        _, _, _, status, _ = metadata_set_update(
            "title", "X", files_list[:1], dry_run=True
        )
        assert "has frontmatter" in status[fp]

    def test_multiple_files(self, mocker):
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            f1 = Path(td) / "a.md"
            f2 = Path(td) / "b.md"
            f1.touch()
            f2.touch()
            mocker.patch(
                "src.file_handle.file_manager.load_frontmatter",
                return_value=({"k": "old"}, ["body"], True),
            )
            mock_reconstruct = mocker.patch("src.file_handle.file_manager.file_reconstruct")

            keys, prev, after, status, action = metadata_set_update(
                "k", "new", [f1, f2], dry_run=True
            )

            assert len(prev) == 2
            assert all(v == "old" for v in prev.values())
            assert all(v == "new" for v in after.values())
            mock_reconstruct.assert_not_called()

    def test_keys_dict_populated(self, mocker, files_list):
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=FRONTMATTER_WITH_KEY,
        )
        fp = files_list[0].as_posix()

        keys_dict, _, _, _, _ = metadata_set_update(
            "title", "X", files_list[:1], dry_run=True
        )
        assert keys_dict[fp] == "title"

    def test_action_change_vs_add(self, mocker, files_list):
        """Verify 'change' when key exists, 'add' when it doesn't."""
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=FRONTMATTER_WITH_KEY,
        )
        _, _, _, _, action_change = metadata_set_update(
            "title", "X", files_list[:1], dry_run=True
        )
        mocker.patch(
            "src.file_handle.file_manager.load_frontmatter",
            return_value=FRONTMATTER_WITHOUT_KEY,
        )
        _, _, _, _, action_add = metadata_set_update(
            "new_key", "Y", files_list[:1], dry_run=True
        )
        assert action_change[files_list[0].as_posix()] == "change"
        assert action_add[files_list[0].as_posix()] == "add"
