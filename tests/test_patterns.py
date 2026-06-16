"""Test Pattern implementations from Evening 10."""

import asyncio
import time
from datetime import datetime

import pytest

from src.factories.fetcher_factory import FetcherFactory
from src.fetchers.base_fetcher import BaseFetcher
from src.fetchers.github_trending_fetcher import GitHubTrendingFetcher
from src.fetchers.hackernews_fetcher import HackerNewsFetcher
from src.models.article import Article
from src.strategies.rate_limit_strategy import SemaphoreStrategy, TokenBucketStrategy
from src.transformers.article_transformer import ArticleTransformer


class InMemoryStorage:
    """Simple storage stub for template-method tests."""

    def __init__(self):
        self.saved = []

    def save(self, articles, filename):
        self.saved.append((filename, list(articles)))


class DummyFetcher(BaseFetcher):
    """Fetcher stub used to verify Template Method and polymorphism behavior."""

    def __init__(self, source_name: str, storage: InMemoryStorage):
        super().__init__(ArticleTransformer(), storage)
        self._source_name = source_name

    async def fetch_articles(self):
        return [
            Article(
                title="T",
                url="https://example.com",
                published_at=datetime.now(),
                source=self._source_name,
            )
        ]

    def get_source_name(self) -> str:
        return self._source_name


def test_factory_pattern():
    """Factory should instantiate fetchers from a type name."""
    transformer = ArticleTransformer()
    storage = InMemoryStorage()

    hn = FetcherFactory.create("hackernews", transformer, storage)
    assert isinstance(hn, HackerNewsFetcher)
    assert hn.get_source_name() == "hackernews"

    gh = FetcherFactory.create("github", transformer, storage)
    assert isinstance(gh, GitHubTrendingFetcher)
    assert gh.get_source_name() == "github_trending"

    available = FetcherFactory.get_available_types()
    assert "hackernews" in available
    assert "github" in available
    assert "github_trending" in available

    config_sources = ["hackernews", "github"]
    fetchers = [
        FetcherFactory.create(source, transformer, storage) for source in config_sources
    ]
    assert len(fetchers) == len(config_sources)


@pytest.mark.asyncio
async def test_template_method_fetch_and_save():
    """Template method should apply common flow for any BaseFetcher."""
    storage = InMemoryStorage()
    fetcher = DummyFetcher("dummy", storage)

    articles = await fetcher.fetch_and_save()

    assert len(articles) == 1
    assert len(storage.saved) == 1
    assert storage.saved[0][0] == "dummy_articles.md"
    assert storage.saved[0][1][0].title == "T"


@pytest.mark.asyncio
async def test_strategy_pattern_rate_limiting():
    """Strategy should enforce concurrency limits consistently."""
    strategy = SemaphoreStrategy(2)

    async def task():
        await strategy.acquire()
        try:
            await asyncio.sleep(0.1)
        finally:
            strategy.release()

    start = time.perf_counter()
    await asyncio.gather(*[task() for _ in range(4)])
    elapsed = time.perf_counter() - start

    assert elapsed >= 0.19
    assert elapsed < 0.5


def test_polymorphic_usage():
    """Function should work with any BaseFetcher implementation."""
    storage = InMemoryStorage()
    transformer = ArticleTransformer()

    def process_fetcher(fetcher: BaseFetcher):
        return fetcher.get_source_name()

    hn = HackerNewsFetcher(transformer=transformer, storage=storage)
    assert process_fetcher(hn) == "hackernews"

    gh = GitHubTrendingFetcher(transformer=transformer, storage=storage)
    assert process_fetcher(gh) == "github_trending"


def test_fetcher_rate_limiter_is_strategy():
    """Fetcher should default to a strategy and accept a custom one."""
    custom = TokenBucketStrategy(100, 60)
    fetcher = HackerNewsFetcher(rate_limiter=custom)

    assert isinstance(fetcher.rate_limiter, TokenBucketStrategy)
    assert fetcher.rate_limiter is custom
