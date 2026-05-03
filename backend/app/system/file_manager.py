"""File system operations — create, delete, move, copy, search."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional

from app.utils.errors import ConfirmationRequired
from app.utils.helpers import sanitize_path
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.system.file_manager")


class FileManager:
    """Manage file system operations safely."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.home()

    def create_file(self, path: str, content: str = "") -> dict[str, str]:
        """Create a new file with optional content."""
        safe_path = sanitize_path(path)
        file_path = self._resolve(safe_path)

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"Created file: {file_path}")
            return {"status": "success", "path": str(file_path)}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def create_directory(self, path: str) -> dict[str, str]:
        """Create a new directory."""
        safe_path = sanitize_path(path)
        dir_path = self._resolve(safe_path)

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
            return {"status": "success", "path": str(dir_path)}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def delete(self, path: str, confirmed: bool = False) -> dict[str, str]:
        """Delete a file or directory (requires confirmation)."""
        safe_path = sanitize_path(path)
        target = self._resolve(safe_path)

        if not confirmed:
            raise ConfirmationRequired(
                "delete", f"Delete {target}? This cannot be undone."
            )

        try:
            if target.is_file():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)
            else:
                return {"status": "error", "message": f"Not found: {target}"}
            logger.info(f"Deleted: {target}")
            return {"status": "success", "message": f"Deleted {target}"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def move(self, source: str, destination: str) -> dict[str, str]:
        """Move a file or directory."""
        src = self._resolve(sanitize_path(source))
        dst = self._resolve(sanitize_path(destination))

        try:
            shutil.move(str(src), str(dst))
            logger.info(f"Moved {src} -> {dst}")
            return {"status": "success", "source": str(src), "destination": str(dst)}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def copy(self, source: str, destination: str) -> dict[str, str]:
        """Copy a file or directory."""
        src = self._resolve(sanitize_path(source))
        dst = self._resolve(sanitize_path(destination))

        try:
            if src.is_file():
                shutil.copy2(str(src), str(dst))
            elif src.is_dir():
                shutil.copytree(str(src), str(dst))
            else:
                return {"status": "error", "message": f"Not found: {src}"}
            logger.info(f"Copied {src} -> {dst}")
            return {"status": "success", "source": str(src), "destination": str(dst)}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def search(
        self, pattern: str, directory: Optional[str] = None, max_results: int = 50
    ) -> list[str]:
        """Search for files matching a pattern."""
        search_dir = self._resolve(directory) if directory else self.base_dir

        results: list[str] = []
        try:
            for match in search_dir.rglob(pattern):
                results.append(str(match))
                if len(results) >= max_results:
                    break
        except PermissionError:
            logger.warning(f"Permission denied searching in {search_dir}")

        logger.info(f"Search '{pattern}': found {len(results)} results")
        return results

    def list_directory(self, path: Optional[str] = None) -> list[dict[str, object]]:
        """List contents of a directory."""
        dir_path = self._resolve(path) if path else self.base_dir

        items: list[dict[str, object]] = []
        try:
            for entry in sorted(dir_path.iterdir()):
                stat = entry.stat()
                items.append({
                    "name": entry.name,
                    "path": str(entry),
                    "is_file": entry.is_file(),
                    "is_dir": entry.is_dir(),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                })
        except PermissionError:
            logger.warning(f"Permission denied listing {dir_path}")

        return items

    def get_info(self, path: str) -> dict[str, object]:
        """Get file or directory information."""
        target = self._resolve(sanitize_path(path))
        if not target.exists():
            return {"status": "error", "message": f"Not found: {target}"}

        stat = target.stat()
        return {
            "status": "success",
            "name": target.name,
            "path": str(target),
            "is_file": target.is_file(),
            "is_dir": target.is_dir(),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "extension": target.suffix,
        }

    def open_in_explorer(self, path: str) -> dict[str, str]:
        """Open a file or folder in the system file explorer."""
        import platform
        import subprocess

        target = self._resolve(sanitize_path(path))
        os_type = platform.system().lower()

        try:
            if os_type == "linux":
                subprocess.Popen(["xdg-open", str(target)])
            elif os_type == "windows":
                os.startfile(str(target))  # type: ignore[attr-defined]
            elif os_type == "darwin":
                subprocess.Popen(["open", str(target)])
            return {"status": "success", "message": f"Opened {target}"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def _resolve(self, path: Optional[str] = None) -> Path:
        """Resolve a path relative to the base directory."""
        if not path:
            return self.base_dir
        p = Path(path)
        if p.is_absolute():
            return p
        return self.base_dir / p
