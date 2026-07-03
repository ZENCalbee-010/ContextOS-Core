"""Shared source formatting for chunks."""

from contextos.memory.models import Chunk
from contextos.memory.repository import SQLiteMemoryRepository


def format_source(
    chunk: Chunk,
    repository: SQLiteMemoryRepository | None = None,
) -> str:
    """Format a chunk source as filepath, section, and page/line metadata."""

    metadata = chunk.metadata or {}
    parts = [_filepath_for_chunk(chunk, metadata, repository)]

    section = metadata.get("section")
    if section:
        parts.append(str(section))

    location = _location(metadata)
    if location:
        parts.append(location)

    return ", ".join(parts)


def preview_text(text: str, *, max_length: int = 160) -> str:
    """Normalize and truncate text for CLI previews."""

    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return f"{normalized[: max_length - 3].rstrip()}..."


def _filepath_for_chunk(
    chunk: Chunk,
    metadata: dict,
    repository: SQLiteMemoryRepository | None,
) -> str:
    filepath = metadata.get("filepath")
    if filepath:
        return str(filepath)

    if repository is not None:
        document = repository.get_document_by_id(chunk.document_id)
        if document is not None:
            return document.filepath

    return f"document:{chunk.document_id}"


def _location(metadata: dict) -> str | None:
    page_number = metadata.get("page_number")
    if page_number is not None:
        return f"page {page_number}"

    start_line = metadata.get("start_line")
    end_line = metadata.get("end_line")
    if start_line is not None and end_line is not None:
        if start_line == end_line:
            return f"line {start_line}"
        return f"lines {start_line}-{end_line}"
    if start_line is not None:
        return f"line {start_line}"

    return None
