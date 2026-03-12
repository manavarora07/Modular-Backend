"""
Loads the raw HTML content from a local file path.
No external HTTP requests are made.
"""

import os


def load_html(html_path: str) -> str:
    """
    Read and return the raw HTML string from a local file.

    Args:
        html_path: Relative or absolute path to the HTML file.

    Returns:
        Raw HTML string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    with open(html_path, encoding="utf-8", errors="replace") as f:
        return f.read()
