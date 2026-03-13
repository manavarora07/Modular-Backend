"""Vector search service.

Current implementation uses Oracle-stored embeddings as the vector source,
exposed through a dedicated vector-db service boundary so this can be swapped
with Pinecone/Qdrant/etc. later without changing search orchestration.
"""

from database.db_client import get_products_with_embeddings_by_category
from search.vector_search import find_similar_by_vector


def search_similar_products(
    *,
    base_product: dict,
    category: str,
    top_n: int,
) -> list[dict]:
    base_embedding = base_product.get("embedding_vector")
    if not base_embedding or not isinstance(base_embedding, list):
        return []

    lookup_key = base_product.get("part_number") or base_product.get("product_name")
    indexed_products = get_products_with_embeddings_by_category(
        category=category,
        exclude_lookup_key=lookup_key,
    )
    if not indexed_products:
        return []

    return find_similar_by_vector(base_product, indexed_products, top_n=top_n)
