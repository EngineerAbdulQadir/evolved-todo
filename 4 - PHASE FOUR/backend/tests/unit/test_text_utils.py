"""Unit tests for text utility functions."""

import pytest
from app.utils.text import strip_emojis, safe_str


class TestStripEmojis:
    """Tests for strip_emojis function."""

    def test_strip_emojis_with_emojis(self):
        """Test removing emojis from text."""
        text = "Hello 😊 World 🌍!"
        result = strip_emojis(text)
        assert result == "Hello  World !"
        assert "😊" not in result
        assert "🌍" not in result

    def test_strip_emojis_no_emojis(self):
        """Test text without emojis remains unchanged."""
        text = "Hello World!"
        result = strip_emojis(text)
        assert result == text

    def test_strip_emojis_empty_string(self):
        """Test empty string returns empty string."""
        assert strip_emojis("") == ""

    def test_strip_emojis_none(self):
        """Test None returns None."""
        assert strip_emojis(None) is None

    def test_strip_emojis_only_emojis(self):
        """Test string with only emojis."""
        text = "😊🌍🎉"
        result = strip_emojis(text)
        assert result == ""

    def test_strip_emojis_mixed_unicode(self):
        """Test removing various Unicode characters."""
        text = "Test™ •√ ✓ 😊"
        result = strip_emojis(text)
        # Only ASCII characters should remain
        assert all(ord(c) < 128 for c in result)

    def test_strip_emojis_preserves_ascii(self):
        """Test that ASCII characters are preserved."""
        text = "ABC123!@# $%^"
        result = strip_emojis(text)
        assert result == text


class TestSafeStr:
    """Tests for safe_str function."""

    def test_safe_str_with_string(self):
        """Test safe_str with regular string."""
        result = safe_str("Hello World")
        assert result == "Hello World"

    def test_safe_str_with_emoji_string(self):
        """Test safe_str removes emojis."""
        result = safe_str("Hello 😊 World")
        assert result == "Hello  World"
        assert "😊" not in result

    def test_safe_str_with_exception(self):
        """Test safe_str with Exception object."""
        exc = Exception("Error 😊 occurred")
        result = safe_str(exc)
        assert "Error" in result
        assert "occurred" in result
        assert "😊" not in result

    def test_safe_str_with_number(self):
        """Test safe_str with number."""
        result = safe_str(123)
        assert result == "123"

    def test_safe_str_with_boolean(self):
        """Test safe_str with boolean."""
        assert safe_str(True) == "True"
        assert safe_str(False) == "False"

    def test_safe_str_with_none(self):
        """Test safe_str with None."""
        result = safe_str(None)
        assert result == "None"

    def test_safe_str_with_dict(self):
        """Test safe_str with dictionary."""
        result = safe_str({"key": "value"})
        assert "key" in result
        assert "value" in result
