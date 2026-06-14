"""Fetch from GitHub Trending."""

from typing import List
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup

from src.fetchers.base_fetcher import BaseFetcher
from src.models.article import Article
from src.storage.markdown_storage import MarkdownStorage
from src.transformers.article_transformer import ArticleTransformer
from src.strategies.rate_limit_strategy import RateLimitStrategy


class GitHubTrendingFetcher(BaseFetcher):
    """Fetch trending repositories from GitHub."""

    def __init__(
        self,
        transformer=None,
        storage=None,
        rate_limiter: RateLimitStrategy | None = None,
    ):
        super().__init__(
            transformer or ArticleTransformer(),
            storage or MarkdownStorage(),
        )
        # Optional rate-limiting strategy (kept for factory/DI consistency).
        self.rate_limiter = rate_limiter

    async def fetch_articles(self) -> List[Article]:
        """Scrape GitHub trending page."""
        url = "https://github.com/trending"
        html = ""

        try:
            if self.rate_limiter:
                await self.rate_limiter.acquire()
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()
        finally:
            if self.rate_limiter:
                self.rate_limiter.release()

        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        repos = soup.select('article.Box-row')

        articles = []
        for repo in repos[:20]:  # Top 20
            # Extract repo info
            title_elem = repo.select_one('h2 a')
            if not title_elem:
                continue

            title = title_elem.text.strip().replace('\n', '').replace(' ', '')
            href = title_elem['href']
            url = f"https://github.com{href}"

            description_elem = repo.select_one('p')
            description = description_elem.text.strip() if description_elem else ''

            stars_elem = repo.select_one('span.d-inline-block.float-sm-right')
            stars = stars_elem.text.strip() if stars_elem else '0'

            article = Article(
                title=title,
                url=url,
                published_at=datetime.now(),
                source='github_trending',
                summary=f"{description} (⭐ {stars})",
                score=0,
            )
            articles.append(article)

        return articles

    def get_source_name(self) -> str:
        """Return source name."""
        return "github_trending"
