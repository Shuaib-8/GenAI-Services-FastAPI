"""Tests for the main module."""

from genai_services import main


def test_main_runs() -> None:
    """Test that main function runs without errors."""
    # Should not raise any exceptions
    main()
