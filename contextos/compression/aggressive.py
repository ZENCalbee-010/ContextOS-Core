"""Aggressive rule-based compression."""

import re

from contextos.compression.base import BaseCompressor, split_paragraphs, split_sentences


HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+\S+")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
SIGNATURE_RE = re.compile(
    r"^\s*(?:export\s+)?(?:(?:async\s+)?(?:def|function)\s+\w+|class\s+\w+|"
    r"(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\()"
)


class AggressiveCompressor(BaseCompressor):
    strategy = "aggressive"

    def _compress(self, text: str) -> str:
        kept: list[str] = []
        seen: set[str] = set()

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if (
                HEADING_RE.match(stripped)
                or BULLET_RE.match(stripped)
                or SIGNATURE_RE.match(stripped)
            ):
                self._append_unique(kept, seen, stripped)

        for paragraph in split_paragraphs(text):
            sentences = split_sentences(paragraph)
            if sentences:
                self._append_unique(kept, seen, sentences[0])

        return "\n".join(kept)

    def _append_unique(self, kept: list[str], seen: set[str], value: str) -> None:
        if value not in seen:
            kept.append(value)
            seen.add(value)
