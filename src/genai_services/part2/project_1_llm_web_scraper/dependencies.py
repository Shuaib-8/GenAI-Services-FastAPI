from fastapi import Body, Request
from loguru import logger

from genai_services.part1.schemas import TextModelRequest

from .scraper import WebScraper

_body_default = Body(...)


def _get_scraper(request: Request) -> WebScraper | None:
    """Retrieve the WebScraper instance from app state."""
    return getattr(request.app.state, "scraper", None)


async def get_urls_content(
    request: Request, body: TextModelRequest = _body_default
) -> str:
    scraper = _get_scraper(request)
    if scraper is None:
        logger.error("Scraper not initialized")
        return ""

    urls: list[str] = scraper.extract_urls(body.prompt)
    if urls:
        try:
            urls_content: str = await scraper.fetch_all(urls)
            return urls_content
        except Exception as e:
            logger.error(f"Error fetching URLs content: {e}")

    return ""
