import pytest

from contextos.parsers import CodeParser, ParsedChunk, TextParser


def test_text_parser_splits_text_into_token_bounded_chunks():
    parser = TextParser(max_tokens=4)

    chunks = parser.parse("one two three\nfour five six\nseven eight")

    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]
    assert [chunk.content for chunk in chunks] == [
        "one two three",
        "four five six",
        "seven eight",
    ]
    assert [chunk.token_count for chunk in chunks] == [3, 3, 2]
    assert chunks[0].start_line == 1
    assert chunks[1].start_line == 2
    assert chunks[2].end_line == 3


def test_markdown_parser_detects_headings_as_sections():
    parser = TextParser(max_tokens=50)
    markdown = """# Overview
Context selection matters.

## Details
Compression comes later.
"""

    chunks = parser.parse(markdown)

    assert len(chunks) == 2
    assert chunks[0].section == "Overview"
    assert chunks[0].content.startswith("# Overview")
    assert chunks[1].section == "Details"
    assert chunks[1].content.startswith("## Details")


def test_code_parser_detects_python_functions_and_classes():
    parser = CodeParser(max_tokens=100)
    code = """import sqlite3

class Repository:
    def init_db(self):
        pass

def helper():
    return 1
"""

    chunks = parser.parse(code)

    assert [chunk.section for chunk in chunks] == ["module", "Repository", "init_db", "helper"]
    assert chunks[1].start_line == 3
    assert chunks[2].content.startswith("def init_db")
    assert chunks[3].end_line == 8


def test_code_parser_detects_javascript_and_typescript_symbols():
    parser = CodeParser(max_tokens=100)
    code = """export function searchIndex() {
  return [];
}

const buildContext = () => {
  return "";
}

export class ContextPack {}
"""

    chunks = parser.parse(code)

    assert [chunk.section for chunk in chunks] == [
        "searchIndex",
        "buildContext",
        "ContextPack",
    ]
    assert chunks[0].start_line == 1
    assert chunks[1].start_line == 5
    assert chunks[2].start_line == 9


def test_code_parser_falls_back_to_line_window_chunks_without_symbols():
    parser = CodeParser(max_tokens=3)

    chunks = parser.parse("alpha beta\ngamma delta\nepsilon")

    assert [chunk.content for chunk in chunks] == [
        "alpha beta",
        "gamma delta\nepsilon",
    ]
    assert all(chunk.section is None for chunk in chunks)


def test_parser_rejects_invalid_max_tokens():
    with pytest.raises(ValueError, match="max_tokens"):
        TextParser(max_tokens=0)


def test_parsed_chunk_supports_optional_page_number():
    chunk = ParsedChunk(
        content="page chunk",
        chunk_index=0,
        token_count=2,
        page_number=3,
    )

    assert chunk.page_number == 3
