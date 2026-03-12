"""
Utilities for converting raw HTML text values into typed Python values.
Handles units like KB, MB, MHz, V, mA, A, etc.
"""

import re


def parse_numeric(raw: str) -> float | None:
    """
    Extract the first numeric value from a raw string.
    Handles common unit suffixes (KB, MB, MHz, mA, A, V, etc.).

    Examples:
        "64 KB"   -> 64.0
        "2.0V"    -> 2.0
        "100 MHz" -> 100.0
        "N/A"     -> None
    """
    if not raw:
        return None
    raw = raw.strip()
    # Find the first floating-point or integer number in the string
    match = re.search(r"[\d]+(?:[.,]\d+)?", raw)
    if not match:
        return None
    try:
        return float(match.group().replace(",", "."))
    except ValueError:
        return None


def parse_memory_kb(raw: str) -> float | None:
    """
    Parse a memory size string and convert to kilobytes.

    Examples:
        "64 KB"  -> 64.0
        "1 MB"   -> 1024.0
        "512"    -> 512.0  (assumed KB)
    """
    if not raw:
        return None
    raw = raw.strip().upper()
    val = parse_numeric(raw)
    if val is None:
        return None
    if "MB" in raw or "MBIT" in raw:
        return val * 1024
    if "GB" in raw:
        return val * 1024 * 1024
    # Default: treat as KB
    return val


def parse_memory_mb(raw: str) -> float | None:
    """
    Parse a memory size string and convert to megabytes.
    """
    kb = parse_memory_kb(raw)
    return kb / 1024 if kb is not None else None


def parse_voltage_range(raw: str) -> tuple[float | None, float | None]:
    """
    Parse a voltage range string into (min, max) tuple.

    Examples:
        "2.0V ~ 3.6V"   -> (2.0, 3.6)
        "1.8V to 5.5V"  -> (1.8, 5.5)
        "3.3V"          -> (3.3, 3.3)
    """
    if not raw:
        return None, None
    raw = raw.strip()
    # Try to find two numbers separated by ~ or to/–
    match = re.search(
        r"([\d.]+)\s*(?:V|v)?\s*(?:~|to|-|–)\s*([\d.]+)\s*(?:V|v)?", raw
    )
    if match:
        return float(match.group(1)), float(match.group(2))
    # Single voltage value
    val = parse_numeric(raw)
    return val, val


def parse_current_a(raw: str) -> float | None:
    """
    Parse a current value and return amperes.

    Examples:
        "500 mA" -> 0.5
        "1.5 A"  -> 1.5
    """
    if not raw:
        return None
    raw = raw.strip().upper()
    val = parse_numeric(raw)
    if val is None:
        return None
    if "MA" in raw or "MILLIAMP" in raw:
        return val / 1000
    return val


def parse_frequency_khz(raw: str) -> float | None:
    """
    Parse a frequency string and return kHz.

    Examples:
        "100 kHz"  -> 100.0
        "1.5 MHz"  -> 1500.0
    """
    if not raw:
        return None
    raw = raw.strip().upper()
    val = parse_numeric(raw)
    if val is None:
        return None
    if "GHZ" in raw:
        return val * 1_000_000
    if "MHZ" in raw:
        return val * 1000
    # Default: assume kHz
    return val


def parse_frequency_mhz(raw: str) -> float | None:
    """Parse a frequency string and return MHz."""
    khz = parse_frequency_khz(raw)
    return khz / 1000 if khz is not None else None


def parse_list(raw: str) -> list[str]:
    """
    Split a comma/slash/space-separated interface or feature string into a list.

    Example:
        "SPI, I2C, UART" -> ["SPI", "I2C", "UART"]
    """
    if not raw:
        return []
    # Split on common delimiters
    items = re.split(r"[,/;]+", raw)
    return [item.strip() for item in items if item.strip()]
