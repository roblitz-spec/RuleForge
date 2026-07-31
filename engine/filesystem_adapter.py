"""FilesystemAdapter — abstract filesystem operations.

Enables testing, dry runs, and future virtual filesystems
without coupling engines to concrete pathlib APIs.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class FilesystemAdapter(ABC):
    """Abstract filesystem for rename operations."""

    @abstractmethod
    def exists(self, path: str) -> bool: ...

    @abstractmethod
    def is_file(self, path: str) -> bool: ...

    @abstractmethod
    def rename(self, src: str, dst: str) -> None: ...

    @abstractmethod
    def delete(self, path: str) -> None: ...


class RealFilesystemAdapter(FilesystemAdapter):
    """Production filesystem adapter using pathlib."""

    def exists(self, path: str) -> bool:
        return Path(path).exists()

    def is_file(self, path: str) -> bool:
        return Path(path).is_file()

    def rename(self, src: str, dst: str) -> None:
        Path(src).rename(Path(dst))

    def delete(self, path: str) -> None:
        Path(path).unlink()
