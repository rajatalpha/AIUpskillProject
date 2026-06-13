"""Main entry point for the news fetcher pipeline."""

import asyncio
import sys

from src.orchestrator import FetchOrchestrator


async def main() -> int:
    print("=" * 60)
    print("  AI Upskill Project — News Fetcher")
    print("  Milestone 1: Async News Fetcher")
    print("=" * 60)
    try:
        articles = await FetchOrchestrator().fetch_all()
        print(f"\n✅ Success! Fetched {len(articles)} articles")
        print("📁 Saved to: data/articles/all_articles.md")
        print("=" * 60)
        return 0
    except Exception as e:
        import traceback

        print(f"\n❌ Error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
