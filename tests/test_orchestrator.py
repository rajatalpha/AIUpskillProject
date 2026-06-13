"""Tests for FetchOrchestrator."""


from src.orchestrator import FetchOrchestrator


async def test_orchestrator_fetch_all():
    orchestrator = FetchOrchestrator()
    articles = await orchestrator.fetch_all()
    # At minimum HackerNews should always return articles
    assert len(articles) > 0
    # All articles must have a valid source tag
    assert all(a.source in {"hackernews", "rss"} for a in articles)
