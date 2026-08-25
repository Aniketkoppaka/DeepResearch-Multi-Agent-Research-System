"""
Source Credibility Scoring Formula Engine.
Calculates normalized credibility C(S) in [0.0, 1.0].
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlparse


HIGH_AUTHORITY_TLDS = {".edu", ".gov", ".mil", ".ac.uk"}
TRUSTED_DOMAINS = {
    "nature.com",
    "science.org",
    "ieee.org",
    "acm.org",
    "arxiv.org",
    "ncbi.nlm.nih.gov",
    "biorxiv.org",
    "medrxiv.org",
    "reuters.com",
    "bloomberg.com",
    "apnews.com",
    "bbc.com",
    "nytimes.com",
    "wsj.com",
    "who.int",
    "un.org",
    "worldbank.org",
}


def calculate_credibility_score(
    url: Optional[str] = None,
    domain: Optional[str] = None,
    author: Optional[str] = None,
    publication_date: Optional[datetime] = None,
    domain_weight: float = 0.5,
    recency_weight: float = 0.3,
    author_weight: float = 0.2,
) -> tuple[float, Dict[str, Any]]:
    """
    Calculate credibility score C(S) = w_dom * S_dom + w_rec * S_rec + w_auth * S_auth
    Returns (score, breakdown_dict).
    """
    # 1. Determine effective domain
    effective_domain = ""
    if domain:
        effective_domain = domain.lower()
    elif url:
        try:
            parsed = urlparse(url)
            effective_domain = parsed.netloc.lower().removeprefix("www.")
        except Exception:

            effective_domain = ""

    # 2. Domain Authority Score S_dom (0.0 to 1.0)
    domain_score = 0.5  # Neutral default
    domain_reason = "Standard web domain"

    if any(effective_domain.endswith(tld) for tld in HIGH_AUTHORITY_TLDS):
        domain_score = 0.95
        domain_reason = "High authority academic or government TLD"
    elif any(trusted in effective_domain for trusted in TRUSTED_DOMAINS):
        domain_score = 0.90
        domain_reason = "Peer-reviewed, institutional, or primary news organization"
    elif effective_domain:
        domain_score = 0.60
        domain_reason = "Standard domain with web identity"

    # 3. Recency Score S_rec (0.0 to 1.0)
    recency_score = 0.5  # Neutral default when unknown
    recency_reason = "Publication date unknown"

    if publication_date:
        now = datetime.now(timezone.utc)
        if publication_date.tzinfo is None:
            pub = publication_date.replace(tzinfo=timezone.utc)
        else:
            pub = publication_date

        age_days = max(0, (now - pub).days)
        if age_days <= 180:  # <= 6 months
            recency_score = 1.0
            recency_reason = "Published within the last 6 months"
        elif age_days <= 365:  # <= 1 year
            recency_score = 0.9
            recency_reason = "Published within the last year"
        elif age_days <= 365 * 3:  # <= 3 years
            recency_score = 0.75
            recency_reason = "Published within the last 3 years"
        elif age_days <= 365 * 5:  # <= 5 years
            recency_score = 0.60
            recency_reason = "Published within the last 5 years"
        else:
            recency_score = 0.40
            recency_reason = "Published more than 5 years ago"

    # 4. Author Attribution Score S_auth (0.0 to 1.0)
    author_score = 0.4  # Neutral when anonymous
    author_reason = "No explicit author attributed"

    if author and author.strip() and author.lower() not in ("unknown", "admin", "editorial team"):
        author_score = 0.85
        author_reason = f"Explicit author credited: {author.strip()}"

    # 5. Composite Score
    total_score = (
        domain_weight * domain_score
        + recency_weight * recency_score
        + author_weight * author_score
    )
    final_score = round(min(1.0, max(0.0, total_score)), 3)

    breakdown = {
        "domain": {
            "value": effective_domain,
            "score": domain_score,
            "weight": domain_weight,
            "reason": domain_reason,
        },
        "recency": {
            "score": recency_score,
            "weight": recency_weight,
            "reason": recency_reason,
        },
        "author": {
            "value": author,
            "score": author_score,
            "weight": author_weight,
            "reason": author_reason,
        },
        "final_score": final_score,
    }

    return final_score, breakdown
