"""
Reads the products CSV file and returns a list of dicts with
product_name, category, and html_path fields.
"""

import csv
import os


def load_product_csv(csv_path: str) -> list[dict]:
    """
    Parse the products CSV file.

    Expected columns: product_name, category, html_path

    Returns:
        List of dicts with keys: product_name, category, html_path
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    products = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            name = row.get("product_name", "").strip()
            category = row.get("category", "").strip().lower()
            html_path = row.get("html_path", "").strip()

            if not name:
                print(f"  [CSV] Row {i}: skipping row with empty product_name")
                continue
            if not html_path:
                print(f"  [CSV] Row {i}: skipping '{name}' — missing html_path")
                continue

            products.append({
                "product_name": name,
                "category": category,
                "html_path": html_path,
            })

    print(f"[CSV] Loaded {len(products)} products from {csv_path}")
    return products
