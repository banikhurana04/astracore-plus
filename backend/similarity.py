"""
ASTraCore++ — similarity metrics on normalized token sequences.

Combines Jaccard similarity on token unigrams and bigrams into one score.
"""

from typing import List, Tuple

Token = Tuple[str, str]


def _token_signature(tokens: List[Token]) -> str:
    """Stable string for each token for set / n-gram operations."""
    return f"{tokens[0]}:{tokens[1]}"


def jaccard_similarity(tokens_a: List[Token], tokens_b: List[Token]) -> float:
    """
    Jaccard index on the multiset of token signatures (as sets of unigrams).
    Returns value in [0.0, 1.0].
    """
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0

    set_a = {_token_signature(t) for t in tokens_a}
    set_b = {_token_signature(t) for t in tokens_b}
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


def _bigrams(tokens: List[Token]) -> List[Tuple[str, str]]:
    """Ordered bigrams as pairs of token signatures."""
    if len(tokens) < 2:
        return []
    sigs = [_token_signature(t) for t in tokens]
    return list(zip(sigs[:-1], sigs[1:]))


def bigram_jaccard_similarity(tokens_a: List[Token], tokens_b: List[Token]) -> float:
    """
    Jaccard index on the set of adjacent token pairs (bigrams).
    """
    ba = _bigrams(tokens_a)
    bb = _bigrams(tokens_b)
    if not ba and not bb:
        return 1.0
    if not ba or not bb:
        return 0.0

    set_a = set(ba)
    set_b = set(bb)
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


def combined_similarity_percent(tokens_a: List[Token], tokens_b: List[Token]) -> float:
    """
    Average of unigram and bigram Jaccard, scaled to 0–100%.
    """
    u = jaccard_similarity(tokens_a, tokens_b)
    b = bigram_jaccard_similarity(tokens_a, tokens_b)
    return round((u + b) / 2.0 * 100.0, 2)
