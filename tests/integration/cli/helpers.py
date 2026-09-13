"""Utility functions used in multiple tests."""

import re
from uuid import UUID


def parse_id(entry: str) -> UUID | None:
    """
    Extract a UUID from a string."
    """
    _uuid = re.compile(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    )
    match = _uuid.search(entry)
    return UUID(match.group(0)) if match else None


def contains_uuid(text: str) -> bool:
    """Determine if a given text indeed contains any UUID"""
    return parse_id(text) is not None
