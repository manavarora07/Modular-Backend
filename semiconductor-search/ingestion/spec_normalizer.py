"""
Converts raw string spec values (from html_parser) into typed Python values.
Produces a fully-normalized product dict ready for database insertion.
"""

from utils.value_parser import (
    parse_memory_kb,
    parse_voltage_range,
    parse_numeric,
    parse_list,
    parse_frequency_mhz,
    parse_frequency_khz,
    parse_current_a,
)
from utils.feature_builder import build_features_text


def normalize_specs(product_name: str, category: str, raw_specs: dict) -> dict:
    """
    Convert raw spec strings into a typed product dict.

    Args:
        product_name: The product identifier.
        category:     The product category key.
        raw_specs:    Dict of canonical_attr -> raw_string from html_parser.

    Returns:
        Fully-typed product dict ready for upsert into the database.
    """
    product: dict = {
        "product_name": product_name,
        "category": category,
    }

    # ── Voltage range (shared across categories) ──────────────────────────────
    for field in ("voltage_range", "input_voltage_range"):
        raw_v = raw_specs.get(field)
        if raw_v:
            vmin, vmax = parse_voltage_range(raw_v)
            if field == "voltage_range":
                product["voltage_min"] = vmin
                product["voltage_max"] = vmax
            else:
                product["voltage_min"] = vmin
                product["voltage_max"] = vmax

    # ── Microcontroller ───────────────────────────────────────────────────────
    if raw_specs.get("architecture"):
        product["architecture"] = raw_specs["architecture"]

    if raw_specs.get("flash_kb"):
        product["flash_kb"] = parse_memory_kb(raw_specs["flash_kb"])

    if raw_specs.get("ram_kb"):
        product["ram_kb"] = parse_memory_kb(raw_specs["ram_kb"])

    if raw_specs.get("gpio_pins"):
        product["gpio_pins"] = int(parse_numeric(raw_specs["gpio_pins"]) or 0) or None

    if raw_specs.get("interfaces"):
        ifaces = parse_list(raw_specs["interfaces"])
        product["interfaces"] = ", ".join(ifaces) if ifaces else None

    if raw_specs.get("max_speed_mhz"):
        product["max_speed_mhz"] = parse_frequency_mhz(raw_specs["max_speed_mhz"])

    # ── Sensor ────────────────────────────────────────────────────────────────
    if raw_specs.get("sensor_type"):
        product["sensor_type"] = raw_specs["sensor_type"]

    if raw_specs.get("measurement_range"):
        product["measurement_range"] = raw_specs["measurement_range"]

    if raw_specs.get("accuracy"):
        product["accuracy"] = raw_specs["accuracy"]

    if raw_specs.get("interface"):
        product["interface"] = raw_specs["interface"]

    if raw_specs.get("output_type"):
        product["output_type"] = raw_specs["output_type"]

    if raw_specs.get("resolution"):
        # Store resolution as accuracy if accuracy not already set
        if not product.get("accuracy"):
            product["accuracy"] = raw_specs["resolution"]

    # ── Power IC ──────────────────────────────────────────────────────────────
    if raw_specs.get("topology"):
        product["topology"] = raw_specs["topology"]

    if raw_specs.get("output_voltage"):
        product["output_voltage"] = raw_specs["output_voltage"]

    if raw_specs.get("output_current_a"):
        product["output_current_a"] = parse_current_a(raw_specs["output_current_a"])

    if raw_specs.get("switching_frequency_khz"):
        product["switching_frequency_khz"] = parse_frequency_khz(raw_specs["switching_frequency_khz"])

    if raw_specs.get("efficiency"):
        product["efficiency"] = raw_specs["efficiency"]

    # ── Memory ────────────────────────────────────────────────────────────────
    if raw_specs.get("memory_type"):
        product["memory_type"] = raw_specs["memory_type"]

    if raw_specs.get("capacity_mb"):
        product["capacity_mb"] = parse_numeric(raw_specs["capacity_mb"])

    if raw_specs.get("speed"):
        product["speed"] = raw_specs["speed"]

    # ── Shared ───────────────────────────────────────────────────────────────
    if raw_specs.get("package_type"):
        product["package_type"] = raw_specs["package_type"]

    if raw_specs.get("temp_range"):
        product["temp_range"] = raw_specs["temp_range"]

    # Build the natural-language features text for embedding
    product["features_text"] = build_features_text(product)

    return product
