"""
Unit tests for source credibility scoring calculation engine.
"""

from datetime import datetime, timezone, timedelta
from app.services.evidence.credibility import calculate_credibility_score


def test_credibility_academic_domain():
    score, breakdown = calculate_credibility_score(
        url="https://cs.stanford.edu/research/paper.pdf",
        author="Prof. John Doe",
        publication_date=datetime.now(timezone.utc) - timedelta(days=30),
    )
    # High credibility (.edu domain + active author + recent)
    assert score >= 0.85
    assert breakdown["domain"]["score"] == 0.95
    assert breakdown["recency"]["score"] == 1.0


def test_credibility_untrusted_anonymous_old_domain():
    score, breakdown = calculate_credibility_score(
        url="https://random-blog-post-123.xyz/article",
        author="unknown",
        publication_date=datetime.now(timezone.utc) - timedelta(days=365 * 6),
    )
    # Lower credibility
    assert score <= 0.60
    assert breakdown["author"]["score"] == 0.40
    assert breakdown["recency"]["score"] == 0.40


def test_credibility_empty_url_safe():
    score, breakdown = calculate_credibility_score(url=None, domain=None)
    assert 0.0 <= score <= 1.0
    assert "domain" in breakdown
