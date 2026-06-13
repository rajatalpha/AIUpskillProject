"""Fetch articles from RSS feeds."""

import asyncio
import re
import time
from datetime import datetime
from typing import List

import feedparser

from src.models.article import Article
from src.storage.markdown_storage import MarkdownStorage


class RSSFetcher:
    """Fetches articles from a single RSS feed URL."""

    def __init__(self, feed_url: str):
        self.feed_url = feed_url
        self.storage = MarkdownStorage()

    async def fetch(self) -> List[Article]:
        print(f"📰 Fetching from RSS: {self.feed_url}")
        loop = asyncio.get_running_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, self.feed_url)
        articles = [a for a in (self._parse_entry(e) for e in feed.entries) if a]
        print(f"✅ Fetched {len(articles)} RSS articles")
        return articles

    def _parse_entry(self, entry) -> Article:
        try:
            url = entry.get("link", "")
            if not url:
                return None
            parsed = entry.get("published_parsed") or entry.get("updated_parsed")
            published_at = (
                datetime.fromtimestamp(time.mktime(parsed))
                if parsed
                else datetime.now()
            )
            raw_summary = entry.get("summary", entry.get("description", ""))
            summary = re.sub(r"<.*?>", "", raw_summary)[:200]
            return Article(
                title=entry.get("title", "No Title"),
                url=url,
                published_at=published_at,
                source="rss",
                summary=summary,
            )
        except Exception as e:
            print(f"⚠️  Failed to parse entry: {e}")
            return None

    async def fetch_and_save(self) -> List[Article]:
        articles = await self.fetch()
        if articles:
            feed_name = self.feed_url.split("//")[-1].split("/")[0]
            self.storage.save(articles, f"rss_{feed_name}_articles.md")
        return articles
