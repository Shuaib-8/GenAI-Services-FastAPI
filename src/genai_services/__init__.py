"""GenAI Services - FastAPI Application."""

from loguru import logger


def main() -> None:
    """Entry point for the genai-services application."""
    logger.info("Starting GenAI Services...")
    logger.debug("Debug mode enabled")
    logger.success("GenAI Services initialized successfully!")
