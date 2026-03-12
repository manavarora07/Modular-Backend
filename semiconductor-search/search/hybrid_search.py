"""
Hybrid search: combines structured Oracle SQL filtering with Python cosine similarity ranking.

Algorithm:
  Step 1 — Structured filter: query Oracle for same-category products that meet
            minimum spec requirements (flash >= base, RAM >= base, etc.).
  Step 2 — Vector re-rank: if embeddings exist, compute cosine similarity in Python
            and sort by score.
  Step 3 — Fallback: if no embeddings, return candidates sorted by a heuristic score.
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
        Dict with base_product, alternatives list, and search_mode.
    """
    # Step 1: Fetch the base product (includes embedding_vector)
    base = get_product_by_name(product_name)
    if not base:
        return {
            "error": f"Product '{product_name}' not found in database.",
            "base_product": None,
            "alternatives": [],
        }

    # Step 2: Structured filtering
    candidates = find_structured_candidates(base, top_n=top_n * 5)

    if not candidates:
        return {
            "base_product": _clean(base),
            "alternatives": [],
            "search_mode": "structured_only",
            "message": "No structured candidates found with matching specs.",
        }

    # Step 3: Vector re-ranking (Python cosine similarity on Oracle CLOB embeddings)
    if base.get("embedding_vector") and isinstance(base["embedding_vector"], list):
        ranked = find_similar_by_vector(base, candidates, top_n=top_n)
        if ranked:
            return {
                "base_product": _clean(base),
                "alternatives": [_clean(r) for r in ranked],
                "search_mode": "hybrid",
                "total_candidates": len(candidates),
            }

    # Fallback: heuristic ranking when embeddings are not yet available
    ranked = _heuristic_rank(base, candidates, top_n)
    return {
        "base_product": _clean(base),
        "alternatives": [_clean(r) for r in ranked],
        "search_mode": "structured_only",
        "total_candidates": len(candidates),
        "note": (
            "Embeddings not generated yet. "
            "Add OPENAI_API_KEY and call /generate-embeddings for better ranking."
        ),
    }


def _heuristic_rank(base: dict, candidates: list[dict], top_n: int) -> list[dict]:
    """Simple spec-match scoring when embeddings are unavailable."""
    def score(c: dict) -> float:
        s = 0.0
        for field in ("architecture", "category", "topology", "sensor_type", "memory_type"):
            bv = (base.get(field) or "").lower()
            cv = (c.get(field) or "").lower()
            if bv and cv and bv == cv:
                s += 2.0
        for field in ("flash_kb", "ram_kb", "gpio_pins", "max_speed_mhz", "output_current_a"):
            bv = base.get(field)
            cv = c.get(field)
            if bv and cv:
                s += min(bv, cv) / max(bv, cv)
        return s

    return sorted(candidates, key=score, reverse=True)[:top_n]


def _clean(product: dict) -> dict:
    """Remove binary/large fields not suitable for JSON serialization."""
    cleaned = {k: v for k, v in product.items() if k != "embedding_vector"}
    for key in ("created_at", "updated_at"):
        if cleaned.get(key) and hasattr(cleaned[key], "isoformat"):
            cleaned[key] = cleaned[key].isoformat()
    return cleaned
