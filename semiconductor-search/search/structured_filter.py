"""
Builds SQL WHERE clauses to filter candidate alternative products
based on numeric spec constraints derived from the base product.

Rules (applied only when the base product has the relevant field):
  - Same category (always required)
  - flash_kb  >= base flash (for microcontrollers)
  - ram_kb    >= base ram   (for microcontrollers)
  - gpio_pins >= base gpio  (for microcontrollers)
  - Same architecture (for microcontrollers, optional)
  - output_current_a >= base current (for power ICs)
"""

import psycopg2.extras
from database.db_client import get_connection


def find_structured_candidates(base_product: dict, top_n: int = 50) -> list[dict]:
    """
    Find products in the same category that meet the minimum spec requirements
    of the base product.

    Args:
        base_product: Full product row dict from the database.
        top_n:        Maximum number of candidates to return.

    Returns:
        List of product dicts (without the embedding_vector column).
    """
    category = base_product.get("category")
    if not category:
        return []

    conditions = ["category = %(category)s", "product_name != %(product_name)s"]
    params: dict = {
        "category": category,
        "product_name": base_product["product_name"],
        "top_n": top_n,
    }

    # ── Microcontroller constraints ───────────────────────────────────────────
    if base_product.get("flash_kb") is not None:
        conditions.append("(flash_kb IS NULL OR flash_kb >= %(flash_kb)s)")
        params["flash_kb"] = base_product["flash_kb"]

    if base_product.get("ram_kb") is not None:
        conditions.append("(ram_kb IS NULL OR ram_kb >= %(ram_kb)s)")
        params["ram_kb"] = base_product["ram_kb"]

    if base_product.get("gpio_pins") is not None:
        conditions.append("(gpio_pins IS NULL OR gpio_pins >= %(gpio_pins)s)")
        params["gpio_pins"] = base_product["gpio_pins"]

    # Note: architecture is NOT a hard filter — we allow cross-architecture alternatives
    # (e.g. ARM Cortex-M3 vs M4 are valid alternatives). Architecture is used for
    # heuristic scoring in hybrid_search._heuristic_rank instead.

    # ── Power IC constraints ──────────────────────────────────────────────────
    if base_product.get("output_current_a") is not None:
        conditions.append(
            "(output_current_a IS NULL OR output_current_a >= %(output_current_a)s)"
        )
        params["output_current_a"] = base_product["output_current_a"]

    if base_product.get("topology"):
        conditions.append(
            "(topology IS NULL OR LOWER(topology) = LOWER(%(topology)s))"
        )
        params["topology"] = base_product["topology"]

    # ── Sensor constraints ────────────────────────────────────────────────────
    if base_product.get("sensor_type"):
        conditions.append(
            "(sensor_type IS NULL OR LOWER(sensor_type) = LOWER(%(sensor_type)s))"
        )
        params["sensor_type"] = base_product["sensor_type"]

    where_clause = " AND ".join(conditions)
    query = f"""
        SELECT id, product_name, category, architecture, flash_kb, ram_kb,
               gpio_pins, voltage_min, voltage_max, interfaces,
               sensor_type, measurement_range, accuracy,
               topology, output_voltage, output_current_a,
               switching_frequency_khz, efficiency,
               memory_type, capacity_mb, speed,
               max_speed_mhz, package_type, temp_range,
               interface, output_type, features_text,
               embedding_vector IS NOT NULL AS has_embedding
        FROM products
        WHERE {where_clause}
        LIMIT %(top_n)s;
    """

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
