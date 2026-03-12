"""
Vector similarity search computed in Python using cosine similarity.

Because Oracle does not have a built-in vector index like pgvector,
embeddings are retrieved from Oracle as JSON CLOBs and cosine similarity
is computed here in Python.

For Oracle 23ai environments with the native VECTOR type, this module can
be swapped for SQL-level similarity using the VECTOR_DISTANCE() function.
"""

import math


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two equal-length vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def find_similar_by_vector(
    base_product: dict,
    candidates: list[dict],
    top_n: int = 10,
) -> list[dict]:
    """
    Rank candidates by cosine similarity to the base product's embedding vector.

    Args:
        base_product: Base product dict with 'embedding_vector' as a list of floats.
        candidates:   List of candidate dicts, each may have 'embedding_vector'.
        top_n:        Number of top results to return.

    Returns:
        Candidates with a 'similarity_score' field, sorted descending.
        Only candidates that have an embedding are included.
        Returns empty list if the base product has no embedding.
    """
    base_embedding = base_product.get("embedding_vector")
    if not base_embedding or not isinstance(base_embedding, list):
        return []

    scored = []
    for candidate in candidates:
        cand_embedding = candidate.get("embedding_vector")
        if not cand_embedding or not isinstance(cand_embedding, list):
            continue
        score = _cosine_similarity(base_embedding, cand_embedding)
        result = {k: v for k, v in candidate.items() if k != "embedding_vector"}
        result["similarity_score"] = round(score, 6)
        scored.append(result)

    scored.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored[:top_n]
