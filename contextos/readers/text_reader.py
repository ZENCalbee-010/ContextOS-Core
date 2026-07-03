"""Plain text and Markdown reader."""

from pathlib import Path

from contextos.readers.base import BaseReader, ReaderResult


class TextReader(BaseReader):
    supported_extensions = frozenset({".txt", ".md", ".markdown"})
    reader_name = "text"

    def read(self, path: str | Path) -> ReaderResult:
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        metadata = self._base_metadata(file_path)
        metadata["format"] = "markdown" if file_path.suffix.lower() in {".md", ".markdown"} else "text"
        return ReaderResult(text=text, metadata=metadata)
