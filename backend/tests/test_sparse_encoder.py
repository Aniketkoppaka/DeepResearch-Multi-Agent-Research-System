"""
Unit tests for SparseEncoder BM25 lexical vector generation.
"""

from app.services.retrieval.sparse_encoder import SparseEncoder


def test_sparse_encoder_deterministic():
    encoder = SparseEncoder()
    text = "Artificial Intelligence and deep machine learning architectures."

    v1 = encoder.encode(text)
    v2 = encoder.encode(text)

    assert v1.indices == v2.indices
    assert v1.values == v2.values
    assert len(v1.indices) > 0
    assert len(v1.values) == len(v1.indices)


def test_sparse_encoder_stopwords_removal():
    encoder = SparseEncoder()
    # Only stopwords
    v = encoder.encode("the and of in for with on at")
    assert v.indices == []
    assert v.values == []


def test_sparse_encoder_batch():
    encoder = SparseEncoder()
    texts = [
        "First research document on multi-agent architectures.",
        "Second document detailing Qdrant vector retrieval.",
    ]
    batch_vectors = encoder.encode_batch(texts)
    assert len(batch_vectors) == 2
    assert len(batch_vectors[0].indices) > 0
    assert len(batch_vectors[1].indices) > 0
