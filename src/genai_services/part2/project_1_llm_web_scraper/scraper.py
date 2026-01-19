import asyncio
import re
from re import Pattern

import aiohttp
from bs4 import BeautifulSoup, Tag
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
        # Match URLs but stop at quotes, whitespace, or common URL terminators
        url_pattern: Pattern[str] = re.compile(r'https?://[^\s"\'<>]+')
        urls: list[str] = url_pattern.findall(url_string)
        # Clean up any trailing punctuation or quotes
        cleaned_urls = []
        for url in urls:
            # Remove trailing quotes, commas, periods, etc.
            url = url.rstrip("\"',.)]}")
            cleaned_urls.append(url)
        return cleaned_urls

    def _remove_wikipedia_elements(self, content: Tag) -> None:
        """Remove Wikipedia-specific HTML elements that contain metadata/navigation."""
        # Remove navigation boxes (navboxes)
        for navbox in content.find_all(
            "div", class_=lambda x: x and "navbox" in x.lower()
        ):
            navbox.decompose()

        # Remove portal boxes
        for portal in content.find_all(
            "div", class_=lambda x: x and "portal" in x.lower()
        ):
            portal.decompose()

        # Remove infoboxes (they're usually at the top and can be redundant)
        for infobox in content.find_all(
            "table", class_=lambda x: x and "infobox" in x.lower()
        ):
            infobox.decompose()

        # Remove reference sections
        section_ids = ["References", "See_also", "External_links", "Further_reading"]
        for section_id in section_ids:
            section = content.find("div", id=section_id)
            if section:
                section.decompose()

        # Remove citation/reference spans
        for ref in content.find_all(
            "span", class_=lambda x: x and "reference" in x.lower()
        ):
            ref.decompose()

        # Remove edit links and other Wikipedia UI elements
        for edit_link in content.find_all("span", class_="mw-editsection"):
            edit_link.decompose()

        # Remove coordinates and other metadata
        for coord in content.find_all("span", id=re.compile(r"coordinates")):
            coord.decompose()

    def _clean_text_patterns(self, text: str) -> str:
        """Clean up Wikipedia metadata patterns from text."""
        # Remove common Wikipedia metadata patterns
        # Pattern: "portalvte", "society portal", etc.
        text = re.sub(
            r"\b(portalvte|society portal|portal\s+vte)\b",
            "",
            text,
            flags=re.IGNORECASE,
        )

        # Remove standalone portal references
        text = re.sub(r"\bportal\s*\b", "", text, flags=re.IGNORECASE)

        # Remove common Wikipedia footer patterns
        text = re.sub(r"vte\s*$", "", text, flags=re.IGNORECASE)

        # Clean up multiple spaces after regex replacements
        return " ".join(text.split())

    def parse_inner_text(self, html_string: str, max_chars: int = 2000) -> str:
        """Parse the inner text of the HTML (assuming the HTML is a Wikipedia page).

        Args:
            html_string: The HTML string to parse
            max_chars: Maximum characters to return (default 2000 to avoid token limit issues)
        """
        soup = BeautifulSoup(html_string, "lxml")
        if content := soup.find("div", id="bodyContent"):  # type: ignore
            self._remove_wikipedia_elements(content)

            # Get text content and normalize whitespace
            text = content.get_text()
            text = " ".join(text.split())

            # Clean up Wikipedia metadata patterns
            text = self._clean_text_patterns(text)

            # Truncate to max_chars to avoid overwhelming the model
            if len(text) > max_chars:
                logger.info(
                    f"Truncating content from {len(text)} to {max_chars} characters"
                )
                text = text[:max_chars] + "... [content truncated]"
            return text
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
