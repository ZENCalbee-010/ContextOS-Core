"""Document readers for local files."""

from contextos.readers.base import BaseReader, ReaderResult
from contextos.readers.detector import get_reader, read_file

__all__ = ["BaseReader", "ReaderResult", "get_reader", "read_file"]
