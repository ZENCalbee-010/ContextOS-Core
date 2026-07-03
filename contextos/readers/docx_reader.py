"""DOCX reader powered by python-docx."""

from pathlib import Path

from docx import Document as DocxDocument

from contextos.readers.base import BaseReader, ReaderResult


class DOCXReader(BaseReader):
    supported_extensions = frozenset({".docx"})
    reader_name = "docx"

    def read(self, path: str | Path) -> ReaderResult:
        file_path = Path(path)
        document = DocxDocument(file_path)
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text]

        metadata = self._base_metadata(file_path)
        metadata.update(
            {
                "paragraph_count": len(document.paragraphs),
                "title": document.core_properties.title or None,
                "author": document.core_properties.author or None,
            }
        )

        return ReaderResult(text="\n".join(paragraphs), metadata=metadata)
