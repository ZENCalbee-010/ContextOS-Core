from contextos.compression import (
    AggressiveCompressor,
    LightCompressor,
    MediumCompressor,
)


def test_light_compressor_removes_repeated_whitespace_and_blank_lines():
    text = "ContextOS    keeps\tcontext.\n\n\n\nSelection   matters."

    result = LightCompressor().compress(text)

    assert result.strategy == "light"
    assert result.compressed == "ContextOS keeps context.\n\nSelection matters."
    assert result.compression_ratio > 0
    assert result.original_length == len(text)
    assert result.compressed_length == len(result.compressed)


def test_light_compressor_optionally_removes_code_comments():
    text = """# module comment
def answer():  # inline comment
    return 42
// js comment
const x = 1; // inline js
"""

    result = LightCompressor(remove_code_comments=True).compress(text)

    assert "# module comment" not in result.compressed
    assert "inline comment" not in result.compressed
    assert "// js comment" not in result.compressed
    assert "inline js" not in result.compressed
    assert "def answer():" in result.compressed
    assert "const x = 1;" in result.compressed


def test_medium_compressor_keeps_top_40_percent_sentences():
    text = (
        "Context selection improves answers. "
        "Context selection reduces noise. "
        "Weather is unrelated. "
        "Selection quality determines usefulness. "
        "Random filler appears here."
    )

    result = MediumCompressor().compress(text)
    kept_sentences = [sentence for sentence in result.compressed.split(".") if sentence.strip()]

    assert result.strategy == "medium"
    assert len(kept_sentences) == 2
    assert "Context selection" in result.compressed
    assert result.compression_ratio > 0


def test_aggressive_compressor_keeps_structural_lines_and_first_sentences():
    text = """# Overview
Context selection matters. Extra detail should be removed.

- Keep this bullet
- Keep another bullet

def build_context(query):
    return query

This paragraph starts important. This sentence is secondary.

class ContextPack:
    pass
"""

    result = AggressiveCompressor().compress(text)

    assert "# Overview" in result.compressed
    assert "- Keep this bullet" in result.compressed
    assert "- Keep another bullet" in result.compressed
    assert "def build_context(query):" in result.compressed
    assert "class ContextPack:" in result.compressed
    assert "Context selection matters." in result.compressed
    assert "This paragraph starts important." in result.compressed
    assert "Extra detail should be removed." not in result.compressed
    assert "This sentence is secondary." not in result.compressed


def test_compression_ratio_for_empty_input_is_zero():
    result = LightCompressor().compress("")

    assert result.compression_ratio == 0.0
    assert result.compressed == ""
