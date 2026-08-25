"""
Sparse Lexical / BM25 Vector Encoder.
Produces hashed term-frequency sparse vectors for lexical keyword matching.
"""

import hashlib
import math
import re
from collections import Counter
from typing import List, Set

from app.services.retrieval.base import SparseVector

STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

# Maximum hash index space for sparse representation (2^20)
SPARSE_INDEX_MAX = 1048576


class SparseEncoder:
    """
    Deterministic BM25 term-frequency sparse vector generator using MurmurHash/MD5 index mapping.
    """

    def __init__(self, k1: float = 1.2, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())
        return [w for w in words if w not in STOP_WORDS and len(w) > 1]

    def _term_to_index(self, term: str) -> int:
        hash_digest = hashlib.md5(term.encode("utf-8")).hexdigest()
        return int(hash_digest[:8], 16) % SPARSE_INDEX_MAX

    def encode(self, text: str) -> SparseVector:
        tokens = self._tokenize(text)
        if not tokens:
            return SparseVector(indices=[], values=[])

        doc_len = len(tokens)
        tf = Counter(tokens)

        # Standard sublinear BM25 TF weight
        indices: List[int] = []
        values: List[float] = []

        term_weights: dict[int, float] = {}

        for term, freq in tf.items():
            idx = self._term_to_index(term)
            # TF scaling formula: tf / (tf + k1 * (1 - b + b * (doc_len / avg_doc_len)))
            # Default avg_doc_len normalized to 100
            denom = freq + self.k1 * (1 - self.b + self.b * (doc_len / 100.0))
            score = (freq * (self.k1 + 1)) / denom

            # Log damping
            weight = math.log(1.0 + score)
            term_weights[idx] = max(term_weights.get(idx, 0.0), weight)

        # Sort by indices for optimal sparse index layout
        sorted_items = sorted(term_weights.items(), key=lambda x: x[0])
        indices = [k for k, _ in sorted_items]
        values = [round(v, 4) for _, v in sorted_items]

        return SparseVector(indices=indices, values=values)

    def encode_batch(self, texts: List[str]) -> List[SparseVector]:
        return [self.encode(t) for t in texts]
