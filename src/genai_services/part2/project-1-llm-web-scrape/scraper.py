import asyncio
import re
from re import Pattern

import aiohttp
from bs4 import BeautifulSoup
from loguru import logger


class WebScraper:
    """Web scraper class with proper async session management."""

    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

    async def __aenter__(self) -> "WebScraper":
        """Async context manager entry."""
        self._session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._session:
            await self._session.close()

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get the session, raising an error if not initialized."""
        if self._session is None:
            raise RuntimeError(
                "Session not initialized. Use 'async with WebScraper()' context manager."
            )
        return self._session

    def extract_urls(self, url_string: str) -> list[str]:
        """Extract the URLs from the HTML via regex pattern matching."""
        url_pattern: Pattern[str] = re.compile(r"https?://[^\s]+")
        urls: list[str] = url_pattern.findall(url_string)
        return urls

    def parse_inner_text(self, html_string: str) -> str:
        """Parse the inner text of the HTML (assuming the HTML is a Wikipedia page)."""
        soup = BeautifulSoup(html_string, "lxml")
        if content := soup.find("div", id="bodyContent"):  # type: ignore
            return content.get_text()
        logger.warning("Could not parse the inner text of the HTML")
        return ""

    async def fetch(self, url: str) -> str:
        """Fetch the HTML from the URL using async context manager."""
        try:
            async with self.session.get(
                url, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                html_string: str = await response.text()
                return self.parse_inner_text(html_string)
        except aiohttp.ClientError as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return ""
        except TimeoutError:
            logger.error(f"Timeout fetching {url}")
            return ""

    async def fetch_all(self, urls: list[str]) -> str:
        """Fetch all the URLs in the list concurrently."""
        tasks = [self.fetch(url) for url in urls]
        results: list[str] = await asyncio.gather(*tasks, return_exceptions=False)

        success_results: list[str] = [result for result in results if result]
        failed_count: int = len(results) - len(success_results)

        if failed_count > 0:
            logger.warning(f"Could not fetch all URLs: {failed_count} URLs failed")

        return " ".join(success_results)


if __name__ == "__main__":
    scraper = WebScraper()

    async def main() -> None:
        async with scraper:
            urls: list[str] = [
                "https://en.wikipedia.org/wiki/Python",
                "https://en.wikipedia.org/wiki/Async",
            ]
            all_content: str = await scraper.fetch_all(urls)
            logger.info(f"All content: {all_content}")

    asyncio.run(main())
