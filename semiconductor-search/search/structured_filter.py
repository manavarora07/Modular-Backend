"""
Structured candidate filtering — delegates to db_client.get_structured_candidates()
which builds the Oracle SQL WHERE clause and executes the query.
"""

from database.db_client import get_structured_candidates


def find_structured_candidates(base_product: dict, top_n: int = 50) -> list[dict]:
    """
    Find products in the same category that meet the minimum spec requirements
    of the base product.

    Args:
        base_product: Full product row dict from the database.
        top_n:        Maximum number of candidates to return.

    Returns:
        List of product dicts (embedding_vector parsed to list if present).
    """
    return get_structured_candidates(base_product, top_n=top_n)
