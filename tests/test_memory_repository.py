import sqlite3

import pytest

from contextos.memory.models import ChunkInput
from contextos.memory.repository import SQLiteMemoryRepository


@pytest.fixture()
def repository(tmp_path):
    repo = SQLiteMemoryRepository(tmp_path / "contextos.sqlite3")
    repo.init_db()
    return repo


def test_init_db_creates_tables_and_indexes(repository):
    with sqlite3.connect(repository.db_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        indexes = {
            row[1]
            for row in connection.execute("PRAGMA index_list('chunks')")
        }
        document_indexes = {
            row[1]
            for row in connection.execute("PRAGMA index_list('documents')")
        }

    assert "documents" in tables
    assert "chunks" in tables
    assert "summaries" in tables
    assert "conversation_history" in tables
    assert "idx_chunks_document_id" in indexes
    assert "idx_documents_sha256" in document_indexes
    assert "idx_documents_filepath" in document_indexes


def test_upsert_document_creates_and_updates_document(repository):
    created = repository.upsert_document(
        "notes/architecture.md",
        "abc123",
        title="Architecture",
        mime_type="text/markdown",
        size_bytes=42,
        metadata={"source": "test"},
    )
    updated = repository.upsert_document(
        "notes/architecture.md",
        "def456",
        title="Updated Architecture",
        mime_type="text/markdown",
        size_bytes=84,
    )

    assert updated.id == created.id
    assert updated.sha256 == "def456"
    assert updated.title == "Updated Architecture"
    assert repository.get_document_by_path("notes/architecture.md") == updated
    assert repository.get_document_by_hash("def456") == updated
    assert repository.get_document_by_hash("abc123") is None


def test_insert_and_fetch_chunks(repository):
    document = repository.upsert_document("docs/context.txt", "hash-1")

    inserted = repository.insert_chunks(
        document.id,
        [
            ChunkInput(
                chunk_index=1,
                content="second chunk",
                token_count=2,
                start_char=10,
                end_char=22,
            ),
            ChunkInput(chunk_index=0, content="first chunk", token_count=2),
        ],
    )

    assert [chunk.chunk_index for chunk in inserted] == [0, 1]
    assert [chunk.content for chunk in repository.get_chunks_by_document(document.id)] == [
        "first chunk",
        "second chunk",
    ]
    assert len(repository.get_all_chunks()) == 2


def test_insert_chunks_replaces_existing_chunks(repository):
    document = repository.upsert_document("docs/context.txt", "hash-1")
    repository.insert_chunks(document.id, [ChunkInput(0, "old")])

    chunks = repository.insert_chunks(
        document.id,
        [ChunkInput(0, "new"), ChunkInput(1, "newer")],
    )

    assert [chunk.content for chunk in chunks] == ["new", "newer"]
    assert len(repository.get_all_chunks()) == 2


def test_insert_chunks_requires_existing_document(repository):
    with pytest.raises(ValueError, match="document_id does not exist"):
        repository.insert_chunks(999, [ChunkInput(0, "orphan")])


def test_save_conversation(repository):
    saved = repository.save_conversation(
        "user",
        "What context matters?",
        metadata={"session": "unit-test"},
    )

    assert saved.id > 0
    assert saved.role == "user"
    assert saved.content == "What context matters?"
    assert saved.metadata == {"session": "unit-test"}
