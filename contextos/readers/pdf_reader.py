"""PDF reader powered by PyMuPDF."""

from pathlib import Path

import fitz

from contextos.readers.base import BaseReader, ReaderResult


class PDFReader(BaseReader):
    supported_extensions = frozenset({".pdf"})
    reader_name = "pdf"

    def read(self, path: str | Path) -> ReaderResult:
        file_path = Path(path)
        page_text: list[str] = []

        with fitz.open(file_path) as document:
            for page in document:
                page_text.append(page.get_text())

            metadata = self._base_metadata(file_path)
            metadata.update(
                {
                    "page_count": document.page_count,
                    "title": document.metadata.get("title") or None,
                    "author": document.metadata.get("author") or None,
                }
            )

        return ReaderResult(text="\n".join(page_text).strip(), metadata=metadata)
