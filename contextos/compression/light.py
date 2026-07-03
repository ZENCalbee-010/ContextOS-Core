"""Light rule-based compression."""

import re

from contextos.compression.base import BaseCompressor


class LightCompressor(BaseCompressor):
    strategy = "light"

    def __init__(self, *, remove_code_comments: bool = False) -> None:
        self.remove_code_comments = remove_code_comments

    def _compress(self, text: str) -> str:
        if self.remove_code_comments:
            text = self._remove_code_comments(text)

        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

    def _remove_code_comments(self, text: str) -> str:
        lines = []
        for line in text.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue
            line = re.sub(r"\s+#.*$", "", line)
            line = re.sub(r"\s+//.*$", "", line)
            lines.append(line)
        return "\n".join(lines)
