"""Keeps one visitor from tying up the server: a simple per-address request limit.

Making a PDF starts a headless browser, which is slow and memory-hungry, so the
PDF endpoints allow only a few requests per address in a short window.
The count lives in memory: it resets on restart and is per server process,
which is enough for a single small server.
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


class Limiter:
    def __init__(self, limit, seconds):
        self.limit, self.seconds = limit, seconds
        self.seen = defaultdict(deque)

    def __call__(self, request: Request):
        address = request.client.host if request.client else "unknown"
        now = time.monotonic()
        recent = self.seen[address]
        while recent and now - recent[0] > self.seconds:
            recent.popleft()
        if len(recent) >= self.limit:
            raise HTTPException(status_code=429, detail="Too many requests. Please wait a few minutes.")
        recent.append(now)
        # Forget addresses that have gone quiet, so the table cannot grow without end
        if len(self.seen) > 5000:
            for key in [k for k, v in self.seen.items() if not v or now - v[-1] > self.seconds]:
                del self.seen[key]


# 8 PDFs per address every 10 minutes
pdf_limit = Limiter(limit=8, seconds=600)
# 10 wrong admin passwords per address every 15 minutes
admin_limit = Limiter(limit=10, seconds=900)
