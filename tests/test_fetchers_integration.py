"""Integration tests for HackerNews + RSS fetchers."""

import asyncio
import time


from src.fetchers.hackernews_fetcher import HackerNewsFetcher
from src.fetchers.rss_fetcher import RSSFetcher

RSS_URL = "https://hnrss.org/frontpage"


async def test_both_fetchers():
    hn = HackerNewsFetcher()
    rss = RSSFetcher(RSS_URL)
    hn_articles = await hn.fetch(limit=5)
    rss_articles = await rss.fetch()
    assert len(hn_articles) > 0
    assert len(rss_articles) > 0


async def test_concurrent_fetching():
    hn = HackerNewsFetcher()
    rss = RSSFetcher(RSS_URL)
    start = time.time()
    hn_articles, rss_articles = await asyncio.gather(hn.fetch(limit=5), rss.fetch())
    elapsed = time.time() - start
    total = len(hn_articles) + len(rss_articles)
    assert total > 0
    assert elapsed < 10.0, f"Concurrent fetch too slow: {elapsed:.2f}s"
