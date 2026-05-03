"""Tests for system control modules."""

import pytest

from app.system.app_control import AppController
from app.system.file_manager import FileManager
from app.system.os_control import OSController
from app.utils.errors import ConfirmationRequired


class TestAppController:
    def test_app_map_exists(self):
        ctrl = AppController()
        assert len(ctrl.app_map) > 0

    def test_is_running_returns_bool(self):
        ctrl = AppController()
        result = ctrl.is_running("nonexistent_app_xyz")
        assert isinstance(result, bool)


class TestOSController:
    def test_shutdown_requires_confirmation(self):
        ctrl = OSController()
        with pytest.raises(ConfirmationRequired):
            ctrl.shutdown(confirmed=False)

    def test_restart_requires_confirmation(self):
        ctrl = OSController()
        with pytest.raises(ConfirmationRequired):
            ctrl.restart(confirmed=False)


class TestFileManager:
    def test_create_and_delete_file(self, tmp_path):
        mgr = FileManager(base_dir=str(tmp_path))
        result = mgr.create_file("test.txt", "hello")
        assert result["status"] == "success"

        info = mgr.get_info("test.txt")
        assert info["is_file"] is True

        result = mgr.delete("test.txt", confirmed=True)
        assert result["status"] == "success"

    def test_create_directory(self, tmp_path):
        mgr = FileManager(base_dir=str(tmp_path))
        result = mgr.create_directory("subdir")
        assert result["status"] == "success"

    def test_delete_requires_confirmation(self, tmp_path):
        mgr = FileManager(base_dir=str(tmp_path))
        mgr.create_file("todelete.txt")
        with pytest.raises(ConfirmationRequired):
            mgr.delete("todelete.txt", confirmed=False)

    def test_move_file(self, tmp_path):
        mgr = FileManager(base_dir=str(tmp_path))
        mgr.create_file("source.txt", "data")
        mgr.create_directory("dest")
        result = mgr.move("source.txt", "dest/source.txt")
        assert result["status"] == "success"

    def test_copy_file(self, tmp_path):
        mgr = FileManager(base_dir=str(tmp_path))
        mgr.create_file("original.txt", "data")
        result = mgr.copy("original.txt", "copied.txt")
        assert result["status"] == "success"

    def test_search_files(self, tmp_path):
        mgr = FileManager(base_dir=str(tmp_path))
        mgr.create_file("findme.txt")
        mgr.create_file("findme2.txt")
        results = mgr.search("findme*")
        assert len(results) >= 2

    def test_list_directory(self, tmp_path):
        mgr = FileManager(base_dir=str(tmp_path))
        mgr.create_file("a.txt")
        mgr.create_file("b.txt")
        items = mgr.list_directory()
        assert len(items) >= 2

    def test_path_traversal_blocked(self, tmp_path):
        mgr = FileManager(base_dir=str(tmp_path))
        with pytest.raises(ValueError, match="Path traversal"):
            mgr.create_file("../../etc/passwd", "hack")
