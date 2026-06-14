"""Base fetcher interface."""
from abc import ABC, abstractmethod
from typing import List

from src.storage.markdown_storage import MarkdownStorage
from src.transformers.article_transformer import ArticleTransformer
from src.models.article import Article


class BaseFetcher(ABC):
    """
    Abstract base class for all article fetchers.

    Defines the contract that all fetchers must follow.
    Enables Open/Closed Principle.
    """

    def __init__(self, transformer=None, storage=None):
        """
        Initialize fetcher with dependencies.

        Args:
            transformer: ArticleTransformer instance
            storage: MarkdownStorage instance
        """
        self.transformer = transformer or ArticleTransformer()
        self.storage = storage or MarkdownStorage()

    @abstractmethod
    async def fetch_articles(self, *args, **kwargs) -> List[Article]:
        """
        Fetch articles from source.

        Must be implemented by subclasses.
        This is the ONLY method that varies by source.

        Returns:
            List of Article objects
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """
        Get the name of this source.

        Returns:
            Source name (e.g., 'hackernews', 'rss', 'github')
        """
        pass

    # Common methods (same for all fetchers)
    
    async def fetch(self, *args, **kwargs) -> List[Article]:
        """
        Legacy public entry point retained for backward compatibility.
        New code should use fetch_articles().
        """
        return await self.fetch_articles(*args, **kwargs)

    async def fetch_and_save(self, *args, **kwargs) -> List[Article]:
        """
        Fetch articles and save to storage.

        Template method - same for all fetchers.
        """
        articles = await self.fetch_articles(*args, **kwargs)

        if articles:
            filename = f"{self.get_source_name()}_articles.md"
            self.storage.save(articles, filename)

        return articles
