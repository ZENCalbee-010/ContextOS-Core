from dataclasses import dataclass

from contextos.context_builder import ContextBuilder
from contextos.memory.models import Chunk, ChunkInput
from contextos.memory.repository import SQLiteMemoryRepository


@dataclass(frozen=True)
class FakeSelection:
    chunk: Chunk
    score: float


def make_chunk(content: str, metadata: dict | None = None) -> Chunk:
    return Chunk(
        id=1,
        document_id=42,
        chunk_index=0,
        content=content,
        token_count=5,
        metadata=metadata,
    )


def test_context_builder_renders_required_prompt_sections():
    chunk = make_chunk(
        "Selection is more important than compression.",
        {
            "filepath": "docs/architecture.md",
            "section": "Core Principle",
            "start_line": 10,
            "end_line": 12,
        },
    )

    prompt = ContextBuilder().build("What matters most?", [chunk])

    assert "SYSTEM:\n\nYou are answering using only the provided context." in prompt
    assert "CONTEXT:" in prompt
    assert "[Chunk 1]" in prompt
    assert (
        "Source: docs/architecture.md, Core Principle, lines 10-12" in prompt
    )
    assert "Content: Selection is more important than compression." in prompt
    assert "QUESTION:\n\nWhat matters most?" in prompt
    assert "INSTRUCTIONS:" in prompt
    assert "- Answer clearly." in prompt
    assert "- Cite source names when possible." in prompt
    assert "- If context is insufficient, say so." in prompt


def test_context_builder_supports_scored_chunk_selections():
    chunk = make_chunk(
        "PDF content.",
        {
            "filepath": "manual.pdf",
            "section": "Setup",
            "page_number": 3,
        },
    )

    prompt = ContextBuilder().build("How do I set it up?", [FakeSelection(chunk, 1.5)])

    assert "[Chunk 1]" in prompt
    assert "Source: manual.pdf, Setup, page 3" in prompt
    assert "Content: PDF content." in prompt


def test_context_builder_resolves_filepath_from_repository(tmp_path):
    repository = SQLiteMemoryRepository(tmp_path / "contextos.sqlite3")
    repository.init_db()
    document = repository.upsert_document("docs/context.md", "hash-1")
    stored_chunks = repository.insert_chunks(
        document.id,
        [
            ChunkInput(
                chunk_index=0,
                content="Stored chunk.",
                token_count=2,
                metadata={"section": "Stored", "start_line": 4, "end_line": 4},
            )
        ],
    )

    prompt = ContextBuilder(repository).build("What is stored?", stored_chunks)

    assert "Source: docs/context.md, Stored, line 4" in prompt


def test_context_builder_handles_empty_context():
    prompt = ContextBuilder().build("Can you answer?", [])

    assert "CONTEXT:\n\n(no context provided)" in prompt
    assert "QUESTION:\n\nCan you answer?" in prompt
