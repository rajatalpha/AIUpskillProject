"""Tests for MarkdownStorage."""

import tempfile
from datetime import datetime

from src.models.article import Article
from src.storage.markdown_storage import MarkdownStorage


def _make_article(n: int = 0) -> Article:
    return Article(
        title=f"Article {n}",
        url=f"https://test{n}.com",
        published_at=datetime(2026, 1, 1),
        source="test",
    )


def test_storage_save_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = MarkdownStorage(tmpdir)
        path = storage.save([_make_article()], "test.md")
        assert path.exists()


def test_storage_file_contains_article():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = MarkdownStorage(tmpdir)
        path = storage.save([_make_article(0)], "test.md")
        content = path.read_text()
        assert "Article 0" in content
        assert "https://test0.com" in content


def test_storage_multiple_articles():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = MarkdownStorage(tmpdir)
        articles = [_make_article(i) for i in range(5)]
        path = storage.save(articles)
        content = path.read_text()
        assert "Article 0" in content
        assert "Article 4" in content


def test_storage_auto_filename():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = MarkdownStorage(tmpdir)
        path = storage.save([_make_article()])
        assert path.exists()
        assert path.name.startswith("articles_")
