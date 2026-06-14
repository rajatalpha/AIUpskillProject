"""Fetch articles from RSS feeds."""

import asyncio
from typing import List

import feedparser

from src.fetchers.base_fetcher import BaseFetcher
from src.models.article import Article
from src.storage.markdown_storage import MarkdownStorage
from src.transformers.article_transformer import ArticleTransformer


class RSSFetcher(BaseFetcher):
    """Fetches articles from a single RSS feed URL."""

    def __init__(self, feed_url: str, transformer=None, storage=None):
        super().__init__(
            transformer or ArticleTransformer(),
            storage or MarkdownStorage(),
        )
        self.feed_url = feed_url

    async def fetch_articles(self, _limit: int | None = None) -> List[Article]:
        print(f"📰 Fetching from RSS: {self.feed_url}")
        loop = asyncio.get_running_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, self.feed_url)
        articles = [a for a in (self._parse_entry(e) for e in feed.entries) if a]
        print(f"✅ Fetched {len(articles)} RSS articles")
        return articles

    def get_source_name(self) -> str:
        return "rss"

    def _parse_entry(self, entry) -> Article | None:
        try:
            url = entry.get("link", "")
            if not url:
                return None
            articles = self.transformer.transform_rss([entry])
            return articles[0] if articles else None
        except Exception as e:
            print(f"⚠️  Failed to parse entry: {e}")
            return None
