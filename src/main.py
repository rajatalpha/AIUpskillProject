"""Main entry point for the news fetcher pipeline."""

# src/main.py
import asyncio

from src.orchestrator import FetchOrchestrator


async def main():
    """Main entry point."""

    # Orchestrator now owns fetcher construction via FetcherFactory.
    orchestrator = FetchOrchestrator()

    # Run
    articles = await orchestrator.fetch_all()
    print(f"✅ Fetched {len(articles)} articles total")


if __name__ == "__main__":
    asyncio.run(main())
