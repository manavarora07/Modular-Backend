"""
Parses a semiconductor product HTML page and extracts key/value spec pairs.

Strategy:
  1. Find all <table> elements that look like specification tables.
  2. Extract (label, value) pairs from table rows (<th>/<td> pairs or two <td> cells).
  3. Use the category configuration's html_spec_map to normalize label names.
  4. Return a flat dict of canonical_attribute -> raw_value_string.
"""

from bs4 import BeautifulSoup
from config.categories_config import CATEGORIES


def parse_product_specs(html: str, category: str) -> dict:
    """
    Parse an HTML page and extract specs for the given category.

    Args:
        html:     Raw HTML string of the product page.
        category: Product category key (must exist in CATEGORIES config).

    Returns:
        Dict mapping canonical attribute names to their raw string values.
        Only attributes defined in the category's html_spec_map are included.
    """
    category = category.lower().strip()
    cat_config = CATEGORIES.get(category, {})
    # Build a lowercase lookup: raw_label_lower -> canonical_attr
    spec_map: dict[str, str] = {
        k.lower(): v for k, v in cat_config.get("html_spec_map", {}).items()
    }

    soup = BeautifulSoup(html, "html.parser")
    raw_specs: dict[str, str] = {}  # canonical_attr -> raw_value_string

    # ── Strategy 1: look for <table> elements ──────────────────────────────────
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            if len(cells) < 2:
                continue

            label = cells[0].get_text(separator=" ", strip=True)
            value = cells[1].get_text(separator=" ", strip=True)

            label_lower = label.lower().rstrip(":").strip()
            canonical = spec_map.get(label_lower)
            if canonical and value:
                # Don't overwrite an already-found value
                if canonical not in raw_specs:
                    raw_specs[canonical] = value

    # ── Strategy 2: look for <dl>/<dt>/<dd> definition lists ──────────────────
    dls = soup.find_all("dl")
    for dl in dls:
        dts = dl.find_all("dt")
        dds = dl.find_all("dd")
        for dt, dd in zip(dts, dds):
            label = dt.get_text(separator=" ", strip=True)
            value = dd.get_text(separator=" ", strip=True)
            label_lower = label.lower().rstrip(":").strip()
            canonical = spec_map.get(label_lower)
            if canonical and value and canonical not in raw_specs:
                raw_specs[canonical] = value

    # ── Strategy 3: look for label/value pairs in divs (common on DigiKey/Mouser) ─
    for div in soup.find_all("div", class_=lambda c: c and "spec" in c.lower()):
        label_tag = div.find(["span", "td", "th", "dt", "label"])
        value_tag = div.find(["span", "td", "dd", "p"], recursive=False)
        if label_tag and value_tag:
            label = label_tag.get_text(strip=True).lower().rstrip(":")
            value = value_tag.get_text(strip=True)
            canonical = spec_map.get(label)
            if canonical and value and canonical not in raw_specs:
                raw_specs[canonical] = value

    return raw_specs
