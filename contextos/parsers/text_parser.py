"""Text and Markdown chunking parser."""

import re

from contextos.parsers.base import BaseParser, ParsedChunk


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


class TextParser(BaseParser):
    """Split plain text or Markdown into token-bounded chunks."""

    def parse(self, text: str) -> list[ParsedChunk]:
        chunks: list[ParsedChunk] = []
        current_lines: list[str] = []
        current_start_line: int | None = None
        current_section: str | None = None
        active_section: str | None = None

        for line_number, line in enumerate(text.splitlines(), start=1):
            heading = HEADING_RE.match(line)
            if heading:
                if current_lines:
                    chunks.append(
                        self._make_chunk(
                            current_lines,
                            len(chunks),
                            current_start_line,
                            line_number - 1,
                            current_section,
                        )
                    )
                    current_lines = []
                    current_start_line = None

                active_section = heading.group(2).strip()

            if current_start_line is None:
                current_start_line = line_number
                current_section = active_section

            candidate = [*current_lines, line]
            if current_lines and self.count_tokens("\n".join(candidate)) > self.max_tokens:
                chunks.append(
                    self._make_chunk(
                        current_lines,
                        len(chunks),
                        current_start_line,
                        line_number - 1,
                        current_section,
                    )
                )
                current_lines = [line]
                current_start_line = line_number
                current_section = active_section
            else:
                current_lines = candidate

        if current_lines:
            chunks.append(
                self._make_chunk(
                    current_lines,
                    len(chunks),
                    current_start_line,
                    len(text.splitlines()) or 1,
                    current_section,
                )
            )

        return chunks

    def _make_chunk(
        self,
        lines: list[str],
        index: int,
        start_line: int | None,
        end_line: int | None,
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
