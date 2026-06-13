"""Fetch top stories from HackerNews."""

import asyncio
from datetime import datetime
from typing import List

import aiohttp

from src.models.article import Article
from src.storage.markdown_storage import MarkdownStorage
from src.utils.rate_limiter import RateLimiter


class HackerNewsFetcher:
    """Fetches top stories from the HackerNews Firebase API."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.storage = MarkdownStorage()
        self.rate_limiter = RateLimiter(max_concurrent=10)

    async def fetch(self, limit: int = 30) -> List[Article]:
        """Fetch top stories from HackerNews concurrently."""
        print(f"📰 Fetching {limit} stories from HackerNews...")
        story_ids = await self._fetch_top_story_ids()
        articles = await self._fetch_stories(story_ids[:limit])
        print(f"✅ Fetched {len(articles)} HackerNews stories")
        return articles

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
        try:
            async with self.rate_limiter:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        data = await response.json()
                        if not data or not data.get("url"):
                            return None
                        return Article(
                            title=data.get("title", "No Title"),
                            url=data["url"],
                            published_at=datetime.fromtimestamp(data.get("time", 0)),
                            source="hackernews",
                            summary=data.get("text", "")[:200],
                            score=data.get("score", 0),
                        )
        except Exception as e:
            print(f"⚠️  Failed to fetch story {story_id}: {e}")
            return None

    async def fetch_and_save(self, limit: int = 30) -> List[Article]:
        """Fetch articles and save them to a markdown file."""
        articles = await self.fetch(limit)
        if articles:
            self.storage.save(articles, "hackernews_articles.md")
        return articles


async def _test_fetch():
    fetcher = HackerNewsFetcher()
    articles = await fetcher.fetch(limit=5)
    print("\n📊 Results:")
    for article in articles:
        print(f"  - {article.title[:60]}...")
    return articles


if __name__ == "__main__":
    asyncio.run(_test_fetch())
