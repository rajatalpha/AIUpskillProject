"""Orchestrate multiple news fetchers."""

import asyncio
from typing import List

from src.factories.fetcher_factory import FetcherFactory
from src.fetchers.base_fetcher import BaseFetcher
from src.models.article import Article
from src.storage.base_storage import ArticleStorage
from src.storage.markdown_storage import MarkdownStorage
from src.transformers.article_transformer import ArticleTransformer


class FetchOrchestrator:
    """Coordinates concurrent fetching from all news sources."""

    def __init__(
        self,
        fetchers: List[BaseFetcher] | None = None,
        storage: ArticleStorage | None = None,
        transformer: ArticleTransformer | None = None,
        source_types: List[str] | None = None,
    ):
        """
        Initialize with injected dependencies.

        If `fetchers` is not provided, fetcher instances are created from source types.
        """
        self.transformer = transformer or ArticleTransformer()
        self.storage = storage or MarkdownStorage()

        if fetchers is not None:
            self.fetchers = fetchers
            return

        source_types = source_types or ["hackernews", "rss", "github_trending"]
        self.fetchers = []
        for source_type in source_types:
            kwargs = {}
            if source_type == "rss":
                kwargs["feed_url"] = "https://hnrss.org/frontpage"
            self.fetchers.append(
                FetcherFactory.create(
                    source_type, self.transformer, self.storage, **kwargs
                )
            )

    async def fetch_all(self) -> List[Article]:
        """Fetch from all sources."""
        all_articles: List[Article] = []

        tasks = [fetcher.fetch_and_save() for fetcher in self.fetchers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for fetcher, result in zip(self.fetchers, results):
            if isinstance(result, Exception):
                print(f"⚠️  {fetcher.get_source_name()} failed: {result}")
                continue
            all_articles.extend(result)

        return all_articles


if __name__ == "__main__":

    async def main():
        orchestrator = FetchOrchestrator()
        articles = await orchestrator.fetch_all()
        for a in articles[:5]:
            print(f"  [{a.source}] {a.title[:60]}...")

    asyncio.run(main())
