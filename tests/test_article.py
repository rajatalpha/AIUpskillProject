"""Tests for Article model."""

from datetime import datetime

import pytest

from src.models.article import Article


def test_article_creation(sample_article_kwargs):
    article = Article(**sample_article_kwargs)
    assert article.title == "Sample article for tests"
    assert article.url == "https://example.com/sample"
    assert article.source == "test"


def test_article_defaults(sample_article_kwargs):
    article = Article(**sample_article_kwargs)
    assert article.summary == ""
    assert article.score == 0


def test_article_empty_title_raises():
    with pytest.raises(ValueError):
        Article(
            title="", url="https://test.com", published_at=datetime.now(), source="test"
        )


def test_article_empty_url_raises():
    with pytest.raises(ValueError):
        Article(title="Title", url="", published_at=datetime.now(), source="test")


def test_article_to_markdown(sample_article_kwargs):
    article = Article(**sample_article_kwargs, summary="A summary")
    md = article.to_markdown()
    assert "Sample article for tests" in md
    assert "https://example.com/sample" in md
    assert "test" in md
    assert "A summary" in md
