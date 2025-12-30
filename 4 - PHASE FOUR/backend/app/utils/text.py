"""Text utility functions for string manipulation and cleaning.

This module provides utilities for text processing, including emoji removal
for Windows console compatibility.
"""

import re


def strip_emojis(text: str) -> str:
    """
    Remove all emojis and special Unicode characters from text.

    This ensures Windows console compatibility by removing characters
    that can't be encoded in cp1252.

    Args:
        text: Input text that may contain emojis

    Returns:
        Text with all emojis removed

    Example:
        >>> strip_emojis("Hello 😊 World!")
        'Hello  World!'
    """
    if not text:
        return text

    # NUCLEAR OPTION: Convert to ASCII and ignore all non-ASCII characters
    # This is the simplest and most reliable way to remove emojis
    try:
        # Encode to ASCII, ignore errors, then decode back to string
        return text.encode('ascii', errors='ignore').decode('ascii')
    except Exception:
        # If even this fails, return empty string
        return ""


def safe_str(obj: any) -> str:
    """
    Convert object to string with emoji removal.

    Safe wrapper around str() that removes emojis from the result.
    Useful for logging and error messages on Windows.

    Args:
        obj: Any object to convert to string

    Returns:
        String representation with emojis removed

    Example:
        >>> safe_str(Exception("Error 😊"))
        'Error '
    """
    return strip_emojis(str(obj))
