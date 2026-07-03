from contextos.formatting import format_source, preview_text
from contextos.memory.models import Chunk, ChunkInput
from contextos.memory.repository import SQLiteMemoryRepository


def test_format_source_uses_repository_filepath_and_line_range(tmp_path):
    repository = SQLiteMemoryRepository(tmp_path / "contextos.sqlite3")
    repository.init_db()
    document = repository.upsert_document("docs/context.md", "hash-1")
    chunk = repository.insert_chunks(
        document.id,
        [
            ChunkInput(
                chunk_index=0,
                content="Context selection matters.",
                token_count=3,
                metadata={"section": "Principle", "start_line": 2, "end_line": 4},
            )
        ],
    )[0]

    assert format_source(chunk, repository) == "docs/context.md, Principle, lines 2-4"


def test_format_source_prefers_metadata_filepath_and_page():
    chunk = Chunk(
        id=1,
        document_id=99,
        chunk_index=0,
        content="PDF content.",
        token_count=2,
        metadata={"filepath": "manual.pdf", "section": "Setup", "page_number": 7},
    )

    assert format_source(chunk) == "manual.pdf, Setup, page 7"


def test_preview_text_normalizes_and_truncates():
    text = "Context\n\nselection    matters for local systems."

    assert preview_text(text, max_length=24) == "Context selection mat..."
