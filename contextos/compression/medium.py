"""Medium rule-based compression using Luhn-style sentence scoring."""

from collections import Counter
import math

from contextos.compression.base import BaseCompressor, WORD_RE, split_sentences


class MediumCompressor(BaseCompressor):
    strategy = "medium"

    def _compress(self, text: str) -> str:
        sentences = split_sentences(text)
        if len(sentences) <= 1:
            return text

        frequencies = self._word_frequencies(text)
        scored = [
            (index, sentence, self._score_sentence(sentence, frequencies))
            for index, sentence in enumerate(sentences)
        ]
        keep_count = max(1, math.ceil(len(sentences) * 0.4))
        selected_indexes = {
            index
            for index, _sentence, _score in sorted(
                scored,
                key=lambda item: item[2],
                reverse=True,
            )[:keep_count]
        }

        return " ".join(
            sentence
            for index, sentence in enumerate(sentences)
            if index in selected_indexes
        )

    def _word_frequencies(self, text: str) -> Counter[str]:
        words = [
            word.lower()
            for word in WORD_RE.findall(text)
            if word.lower() not in STOPWORDS
        ]
        return Counter(words)

    def _score_sentence(self, sentence: str, frequencies: Counter[str]) -> float:
        words = [word.lower() for word in WORD_RE.findall(sentence)]
        important_words = [word for word in words if word not in STOPWORDS]
        if not important_words:
            return 0.0
        return sum(frequencies[word] for word in important_words) / len(important_words)


STOPWORDS = {
    "and",
    "are",
    "but",
    "for",
    "from",
    "into",
    "not",
    "the",
    "this",
    "that",
    "with",
    "you",
    "your",
}
