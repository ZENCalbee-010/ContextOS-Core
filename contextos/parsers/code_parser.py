"""Regex-based code chunking parser."""

import re

from contextos.parsers.base import BaseParser, ParsedChunk


PYTHON_SYMBOL_RE = re.compile(r"^\s*(?:async\s+def|def|class)\s+([A-Za-z_]\w*)")
JS_TS_SYMBOL_RE = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?(?:function|class)\s+([A-Za-z_$][\w$]*)"
)
ARROW_SYMBOL_RE = re.compile(
    r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\("
)


class CodeParser(BaseParser):
    """Split source code around simple class and function declarations."""

    def parse(self, text: str) -> list[ParsedChunk]:
        lines = text.splitlines()
        symbol_starts = self._find_symbol_starts(lines)

        if not symbol_starts:
            return self._chunk_line_window(lines)

        ranges: list[tuple[int, int, str | None]] = []
        if symbol_starts[0][0] > 1:
            ranges.append((1, symbol_starts[0][0] - 1, "module"))

        for index, (start_line, section) in enumerate(symbol_starts):
            next_start = (
                symbol_starts[index + 1][0]
                if index + 1 < len(symbol_starts)
                else len(lines) + 1
            )
            ranges.append((start_line, next_start - 1, section))

        chunks: list[ParsedChunk] = []
        for start_line, end_line, section in ranges:
            block_lines = lines[start_line - 1 : end_line]
            chunks.extend(
                self._chunk_line_window(
                    block_lines,
                    start_line_offset=start_line,
                    section=section,
                    start_index=len(chunks),
                )
            )

        return self._renumber(chunks)

    def _find_symbol_starts(self, lines: list[str]) -> list[tuple[int, str]]:
        starts: list[tuple[int, str]] = []
        for line_number, line in enumerate(lines, start=1):
            match = (
                PYTHON_SYMBOL_RE.match(line)
                or JS_TS_SYMBOL_RE.match(line)
                or ARROW_SYMBOL_RE.match(line)
            )
            if match:
                starts.append((line_number, match.group(1)))
        return starts

    def _chunk_line_window(
        self,
        lines: list[str],
        *,
        start_line_offset: int = 1,
        section: str | None = None,
        start_index: int = 0,
    ) -> list[ParsedChunk]:
        chunks: list[ParsedChunk] = []
        current_lines: list[str] = []
        current_start_line = start_line_offset

        for relative_index, line in enumerate(lines, start=0):
            line_number = start_line_offset + relative_index
            candidate = [*current_lines, line]
            if current_lines and self.count_tokens("\n".join(candidate)) > self.max_tokens:
                chunks.append(
                    self._make_chunk(
                        current_lines,
                        start_index + len(chunks),
                        current_start_line,
                        line_number - 1,
                        section,
                    )
                )
                current_lines = [line]
                current_start_line = line_number
            else:
                current_lines = candidate

        if current_lines:
            chunks.append(
                self._make_chunk(
                    current_lines,
                    start_index + len(chunks),
                    current_start_line,
                    start_line_offset + len(lines) - 1,
                    section,
                )
            )

        return chunks

    def _make_chunk(
        self,
        lines: list[str],
        index: int,
        start_line: int,
        end_line: int,
        section: str | None,
    ) -> ParsedChunk:
        content = "\n".join(lines).strip()
        return ParsedChunk(
            content=content,
            chunk_index=index,
            start_line=start_line,
            end_line=end_line,
            section=section,
            token_count=self.count_tokens(content),
        )
