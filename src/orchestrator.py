"""Orchestrate multiple news fetchers."""

import asyncio
from typing import List

from src.fetchers.hackernews_fetcher import HackerNewsFetcher
from src.fetchers.rss_fetcher import RSSFetcher
from src.models.article import Article
from src.storage.markdown_storage import MarkdownStorage


class FetchOrchestrator:
    """Coordinates concurrent fetching from all news sources."""

    def __init__(self):
        self.storage = MarkdownStorage()
        self.fetchers = [
            ("HackerNews", HackerNewsFetcher()),
            ("HN RSS", RSSFetcher("https://hnrss.org/frontpage")),
        ]

    async def fetch_all(self) -> List[Article]:
        print(f"\n🚀 Starting fetch from {len(self.fetchers)} sources...")

        tasks = [
            f.fetch(limit=30) if isinstance(f, HackerNewsFetcher) else f.fetch()
            for _, f in self.fetchers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_articles: List[Article] = []
        for (name, _), result in zip(self.fetchers, results):
            if isinstance(result, Exception):
                print(f"⚠️  {name} failed: {result}")
            else:
                print(f"✅ {name}: {len(result)} articles")
                all_articles.extend(result)

        if all_articles:
            self.storage.save(all_articles, "all_articles.md")

        print(
            f"\n🎉 Total: {len(all_articles)} articles from {len(self.fetchers)} sources"
        )
        return all_articles


if __name__ == "__main__":

    async def main():
        orchestrator = FetchOrchestrator()
        articles = await orchestrator.fetch_all()
        for a in articles[:5]:
            print(f"  [{a.source}] {a.title[:60]}...")

    asyncio.run(main())
