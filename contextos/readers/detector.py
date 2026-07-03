"""Reader detection by file extension."""

from pathlib import Path

from contextos.readers.base import BaseReader, ReaderResult
from contextos.readers.code_reader import CodeReader
from contextos.readers.docx_reader import DOCXReader
from contextos.readers.pdf_reader import PDFReader
from contextos.readers.text_reader import TextReader


READERS: tuple[BaseReader, ...] = (
    PDFReader(),
    DOCXReader(),
    TextReader(),
    CodeReader(),
)


def get_reader(path: str | Path) -> BaseReader | None:
    """Return the first reader that supports the file extension."""

    file_path = Path(path)
    for reader in READERS:
        if reader.can_read(file_path):
            return reader
    return None


def read_file(path: str | Path) -> ReaderResult:
    """Read a supported file or return an unsupported result gracefully."""

    file_path = Path(path)
    reader = get_reader(file_path)
    if reader is None:
        return ReaderResult(
            text="",
            metadata={
                "filepath": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix.lower(),
                "reader": None,
            },
            supported=False,
            error=f"Unsupported file type: {file_path.suffix.lower() or '<none>'}",
        )

    try:
        return reader.read(file_path)
    except OSError as exc:
        return ReaderResult(
            text="",
            metadata={
                "filepath": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix.lower(),
                "reader": reader.reader_name,
            },
            supported=True,
            error=str(exc),
        )
