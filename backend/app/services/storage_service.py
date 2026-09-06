from __future__ import annotations

import hashlib
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO

from app.core.config import get_settings


class StorageService(ABC):
    @abstractmethod
    def save(self, user_id: int, filename: str, stream: BinaryIO) -> dict:
        """Save an incoming file stream and return metadata dict with keys:
        - storage_path: internal key
        - file_url: public or presigned URL (may be empty/null)
        - file_size: int
        """

    @abstractmethod
    def delete(self, storage_path: str) -> None:
        """Delete stored file identified by storage_path"""


class UploadTooLargeError(Exception):
    pass


class LocalStorageService(StorageService):
    def __init__(self, base_dir: str | None = None):
        settings = get_settings()
        self.base_dir = Path(base_dir or settings.uploads_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def _user_dir(self, user_id: int) -> Path:
        p = self.base_dir / str(user_id)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def save(self, user_id: int, filename: str, stream: BinaryIO) -> dict:
        # Save to user directory with secure name: use provided filename but prefix with hash to reduce collisions
        user_dir = self._user_dir(user_id)
        # Create a temp filename
        safe_name = f"{hashlib.sha256(filename.encode()).hexdigest()[:8]}_{Path(filename).name}"
        dest = user_dir / safe_name
        hash_sha256 = hashlib.sha256()
        total = 0
        settings = get_settings()
        max_bytes = getattr(settings, "max_upload_size_bytes", None)
        # Stream write with size enforcement
        with open(dest, "wb") as f:
            while True:
                chunk = stream.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                hash_sha256.update(chunk)
                total += len(chunk)
                if max_bytes is not None and total > max_bytes:
                    # remove partial file
                    try:
                        f.close()
                        dest.unlink(missing_ok=True)
                    except Exception:
                        pass
                    raise UploadTooLargeError("File exceeds maximum allowed size")
        checksum = hash_sha256.hexdigest()
        # For local storage, do NOT expose absolute filesystem path as file_url. file_url will be a safe identifier (filename)
        return {
            "storage_path": str(dest.resolve()),
            "file_url": safe_name,
            "file_size": total,
            "checksum_sha256": checksum,
        }

    def delete(self, storage_path: str) -> None:
        try:
            p = Path(storage_path)
            if p.exists():
                p.unlink()
        except Exception:
            # Log at service level if available
            pass
