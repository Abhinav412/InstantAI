"""Web Crawling tool."""

import asyncio
from typing import Type

from crawl4ai import AsyncWebCrawler
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class CrawlInput(BaseModel):
    """Input URL that needs to be crawled."""

    url: str = Field(description="The URL to crawl and extract content from.")


class Crawl4AICrawler(BaseTool):
    """Web Crawler tool using Crawl4AI."""

    name: str = "crawl_web_page"
    description: str = "Useful for extracting detailed content from a specific URL. Use this after searching to read the page content."
    args_schema: Type[BaseModel] = CrawlInput

    def _run(self, url: str) -> str:
        return asyncio.run(self._arun(url))

    async def _arun(self, url: str) -> str:
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.crawl(url=url)
            if not result.success:
                return f"Failed to crawl {url}: {result.error_message}"

            return result.markdown
