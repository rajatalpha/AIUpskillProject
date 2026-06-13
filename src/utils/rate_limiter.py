"""Simple semaphore-based rate limiter."""

import asyncio


class RateLimiter:
    """Limits concurrent async operations via a semaphore."""

    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self):
        await self.semaphore.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.semaphore.release()
