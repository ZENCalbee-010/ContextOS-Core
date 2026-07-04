from contextos.indexer import FileIndexer, sha256_file
from contextos.memory.repository import SQLiteMemoryRepository


def make_indexer(tmp_path):
    repository = SQLiteMemoryRepository(tmp_path / "contextos.sqlite3")
    repository.init_db()
    return FileIndexer(repository, max_tokens_per_chunk=20), repository


def test_new_file_import(tmp_path):
    indexer, repository = make_indexer(tmp_path)
    path = tmp_path / "notes.md"
    path.write_text("# Context\n\nSelection beats compression.", encoding="utf-8")

    result = indexer.index_file(path)
    document = repository.get_document_by_path(path)
    chunks = repository.get_chunks_by_document(document.id)

    assert result.status == "imported"
    assert result.sha256 == sha256_file(path)
    assert result.document_id == document.id
    assert result.chunk_count == 1
    assert {"compression", "context", "selection"}.issubset(
        document.metadata["keywords"]
    )
    assert document.metadata["structure"] == ["Context"]
    assert chunks[0].metadata["section"] == "Context"
    assert {"compression", "context", "selection"}.issubset(
        chunks[0].metadata["keywords"]
    )


def test_unchanged_file_skip(tmp_path):
    indexer, repository = make_indexer(tmp_path)
    path = tmp_path / "notes.txt"
    path.write_text("stable local context", encoding="utf-8")

    first = indexer.index_file(path)
    second = indexer.index_file(path)
    document = repository.get_document_by_path(path)

    assert first.status == "imported"
    assert second.status == "skipped"
    assert second.document_id == first.document_id
    assert second.sha256 == document.sha256
    assert second.chunk_count == 1


def test_changed_file_reprocesses_and_replaces_chunks(tmp_path):
    indexer, repository = make_indexer(tmp_path)
    path = tmp_path / "module.py"
    path.write_text(
        "def first():\n    return 'old'\n",
        encoding="utf-8",
    )

    first = indexer.index_file(path)
    first_document = repository.get_document_by_path(path)
    first_chunks = repository.get_chunks_by_document(first_document.id)

    path.write_text(
        "class Second:\n    pass\n\ndef third():\n    return 'new'\n",
        encoding="utf-8",
    )
    second = indexer.index_file(path)
    second_document = repository.get_document_by_path(path)
    second_chunks = repository.get_chunks_by_document(second_document.id)

    assert first.status == "imported"
    assert second.status == "imported"
    assert second.document_id == first.document_id
    assert second.sha256 != first.sha256
    assert first_document.id == second_document.id
    assert [chunk.content for chunk in first_chunks] == ["def first():\n    return 'old'"]
    assert [chunk.metadata["section"] for chunk in second_chunks] == [
        "Second",
        "third",
    ]
    assert len(second_chunks) == 2
