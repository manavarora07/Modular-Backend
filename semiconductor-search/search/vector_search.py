"""
Performs vector similarity search using pgvector's cosine distance operator.
Requires the base product to have an embedding vector stored.
"""

import psycopg2.extras
from database.db_client import get_connection


def find_similar_by_vector(
    base_product_name: str,
    candidate_names: list[str],
    top_n: int = 10,
) -> list[dict]:
    """
    Rank the given candidate products by cosine similarity to the base product's
    embedding vector.

    Args:
        base_product_name: Name of the reference product.
        candidate_names:   List of product names to rank.
        top_n:             Number of top results to return.

    Returns:
        List of dicts with product fields + 'similarity_score' (0-1, higher=better).
        Returns empty list if base product has no embedding.
    """
    if not candidate_names:
        return []

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Fetch the base product's embedding
            cur.execute(
                "SELECT embedding_vector FROM products WHERE product_name = %s;",
                (base_product_name,)
            )
            row = cur.fetchone()
            if not row or row["embedding_vector"] is None:
                return []

            base_embedding = row["embedding_vector"]

            # Find cosine similarity (1 - cosine_distance) for each candidate
            # pgvector operator <=> = cosine distance (0 = identical, 2 = opposite)
            cur.execute("""
                SELECT
                    id, product_name, category, architecture, flash_kb, ram_kb,
                    gpio_pins, voltage_min, voltage_max, interfaces,
                    sensor_type, measurement_range, accuracy,
                    topology, output_voltage, output_current_a,
                    switching_frequency_khz, efficiency,
                    memory_type, capacity_mb, speed,
                    max_speed_mhz, package_type, temp_range,
                    interface, output_type, features_text,
                    1 - (embedding_vector <=> %(base_emb)s::vector) AS similarity_score
                FROM products
                WHERE product_name = ANY(%(candidates)s)
                  AND embedding_vector IS NOT NULL
                ORDER BY similarity_score DESC
                LIMIT %(top_n)s;
            """, {
                "base_emb": base_embedding,
                "candidates": candidate_names,
                "top_n": top_n,
            })
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
