"""Fetch top stories from HackerNews."""

import asyncio
from typing import List

import aiohttp

from src.models.article import Article
from src.strategies.rate_limit_strategy import SemaphoreStrategy
from src.fetchers.base_fetcher import BaseFetcher


class HackerNewsFetcher(BaseFetcher):
    """Fetches top stories from the HackerNews Firebase API."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self, transformer=None, storage=None, rate_limiter=None):
        super().__init__(transformer, storage)
        self.rate_limiter = rate_limiter or SemaphoreStrategy()

    async def fetch_articles(self, limit: int = 30) -> List[Article]:
        """Fetch top stories from HackerNews concurrently."""
        print(f"📰 Fetching {limit} stories from HackerNews...")
        story_ids = await self._fetch_top_story_ids()
        articles = await self._fetch_stories(story_ids[:limit])
        print(f"✅ Fetched {len(articles)} HackerNews stories")
        return articles

    def get_source_name(self) -> str:
        return "hackernews"

    async def _fetch_top_story_ids(self) -> List[int]:
        url = f"{self.BASE_URL}/topstories.json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    async def _fetch_stories(self, story_ids: List[int]) -> List[Article]:
        tasks = [self._fetch_story(sid) for sid in story_ids]
        stories = await asyncio.gather(*tasks)
        return [s for s in stories if s is not None]

    async def _fetch_story(self, story_id: int):
        url = f"{self.BASE_URL}/item/{story_id}.json"
        acquired = False
        try:
            await self.rate_limiter.acquire()
            acquired = True
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    if not data or not data.get("url"):
                        return None
                    articles = self.transformer.transform_hackernews([data])
                    return articles[0] if articles else None
        except Exception as e:
            print(f"⚠️  Failed to fetch story {story_id}: {e}")
            return None
        finally:
            if acquired:
                self.rate_limiter.release()


async def _test_fetch():
    fetcher = HackerNewsFetcher()
    articles = await fetcher.fetch(limit=5)
    print("\n📊 Results:")
    for article in articles:
        print(f"  - {article.title[:60]}...")
    return articles


if __name__ == "__main__":
    asyncio.run(_test_fetch())
