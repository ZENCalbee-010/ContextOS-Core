"""Source code file reader."""

from pathlib import Path

from contextos.readers.base import BaseReader, ReaderResult


class CodeReader(BaseReader):
    supported_extensions = frozenset({
        ".py",
        ".js",
        ".ts",
        ".html",
        ".css",
        ".json",
    })
    reader_name = "code"

    def read(self, path: str | Path) -> ReaderResult:
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        metadata = self._base_metadata(file_path)
        metadata["language"] = self._language_for_extension(file_path.suffix.lower())
        return ReaderResult(text=text, metadata=metadata)

    def _language_for_extension(self, extension: str) -> str:
        return {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".html": "html",
            ".css": "css",
            ".json": "json",
        }[extension]
