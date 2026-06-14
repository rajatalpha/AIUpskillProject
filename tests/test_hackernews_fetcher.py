"""Tests for HackerNews fetcher."""

import time

from src.fetchers.hackernews_fetcher import HackerNewsFetcher
from src.models.article import Article


async def test_fetch_returns_articles():
    fetcher = HackerNewsFetcher()
    articles = await fetcher.fetch(limit=5)
    assert len(articles) > 0
    assert len(articles) <= 5
    for article in articles:
        assert isinstance(article, Article)
        assert article.title
        assert article.url
        assert article.source == "hackernews"


async def test_fetch_concurrent():
    fetcher = HackerNewsFetcher()
    start = time.time()
    articles = await fetcher.fetch(limit=10)
    elapsed = time.time() - start
    assert elapsed < 5.0, f"Fetch too slow: {elapsed:.2f}s"
    assert len(articles) > 0


async def test_hackernews_fetcher_uses_transformer():
    """Verify fetcher returns Articles produced by ArticleTransformer."""
    fetcher = HackerNewsFetcher()
    articles = await fetcher.fetch(limit=5)
    assert len(articles) > 0
    assert all(hasattr(a, "title") for a in articles)
    assert all(isinstance(a, Article) for a in articles)
