"""
Hybrid search: combines structured SQL filtering with vector similarity ranking.

Algorithm:
  Step 1 — Structured filter: find all products in the same category that meet
            minimum spec requirements (same arch, flash >= base flash, etc.).
  Step 2 — Vector re-rank: if embeddings are available, re-rank the candidates
            by cosine similarity to the base product.
  Step 3 — Fallback: if no embeddings exist, return the structured candidates
            sorted by a simple spec-match heuristic score.
"""

from database.db_client import get_product_by_name
from search.structured_filter import find_structured_candidates
from search.vector_search import find_similar_by_vector
from config.settings import TOP_N_RESULTS


def find_alternatives(product_name: str, top_n: int = TOP_N_RESULTS) -> dict:
    """
    Find alternative semiconductor products for the given product name.

    Args:
        product_name: Exact product name as stored in the database.
        top_n:        Number of alternatives to return.

    Returns:
        Dict with:
          - base_product: the reference product's spec dict
          - alternatives: ranked list of alternative products
          - search_mode:  "hybrid" | "structured_only" (depending on embeddings)
    """
    # Step 1: Fetch the base product
    base = get_product_by_name(product_name)
    if not base:
        return {
            "error": f"Product '{product_name}' not found in database.",
            "base_product": None,
            "alternatives": [],
        }

    # Step 2: Structured filtering — get candidates from same category
    # Fetch more than top_n so vector re-ranking has enough to work with
    candidates = find_structured_candidates(base, top_n=top_n * 5)

    if not candidates:
        return {
            "base_product": _clean(base),
            "alternatives": [],
            "search_mode": "structured_only",
            "message": "No structured candidates found with matching specs.",
        }

    candidate_names = [c["product_name"] for c in candidates]

    # Step 3: Vector re-ranking (requires embeddings to be generated first)
    base_has_embedding = base.get("embedding_vector") is not None
    if base_has_embedding:
        ranked = find_similar_by_vector(product_name, candidate_names, top_n=top_n)
        if ranked:
            return {
                "base_product": _clean(base),
                "alternatives": [_clean(r) for r in ranked],
                "search_mode": "hybrid",
                "total_candidates": len(candidates),
            }

    # Fallback: heuristic ranking when no embeddings are available
    ranked = _heuristic_rank(base, candidates, top_n)
    return {
        "base_product": _clean(base),
        "alternatives": [_clean(r) for r in ranked],
        "search_mode": "structured_only",
        "total_candidates": len(candidates),
        "note": "Embeddings not generated yet. Add OPENAI_API_KEY and call /generate-embeddings for better ranking.",
    }


def _heuristic_rank(base: dict, candidates: list[dict], top_n: int) -> list[dict]:
    """
    Simple heuristic scoring when vector embeddings are not available.
    Score = number of spec fields that closely match the base product.
    """
    def score(candidate: dict) -> float:
        s = 0.0
        for field in ("architecture", "category", "topology", "sensor_type", "memory_type"):
            bv = (base.get(field) or "").lower()
            cv = (candidate.get(field) or "").lower()
            if bv and cv and bv == cv:
                s += 2.0

        for field in ("flash_kb", "ram_kb", "gpio_pins", "max_speed_mhz", "output_current_a"):
            bv = base.get(field)
            cv = candidate.get(field)
            if bv and cv:
                ratio = min(bv, cv) / max(bv, cv)
                s += ratio  # 0..1 closeness bonus

        return s

    scored = sorted(candidates, key=score, reverse=True)
    return scored[:top_n]


def _clean(product: dict) -> dict:
    """Remove binary/large fields not suitable for JSON serialization."""
    cleaned = {k: v for k, v in product.items() if k != "embedding_vector"}
    # Convert datetime objects to ISO strings for JSON
    for key in ("created_at", "updated_at"):
        if cleaned.get(key) and hasattr(cleaned[key], "isoformat"):
            cleaned[key] = cleaned[key].isoformat()
    return cleaned
