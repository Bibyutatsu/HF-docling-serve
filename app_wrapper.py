"""Wrapper to add health-check, rate limiting, and concurrency control for HF Spaces."""

import asyncio
import os
import time
from collections import defaultdict

from docling_serve.app import create_app
from fastapi import Request
from starlette.responses import JSONResponse, RedirectResponse

# --- Configuration (override via ENV) ---
RATE_LIMIT_PER_MINUTE = int(os.environ.get("DOCLING_WRAPPER_RATE_LIMIT", "2"))
MAX_CONCURRENT_TASKS = int(os.environ.get("DOCLING_WRAPPER_MAX_CONCURRENT", "3"))

# Heavy endpoint prefixes that need protection
HEAVY_PREFIXES = ("/v1/convert", "/v1/chunk")

# --- App Setup ---
app = create_app()

# --- Simple In-Memory Sliding Window Rate Limiter ---
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


def _is_rate_limited(client_ip: str) -> bool:
    """Check if client_ip has exceeded RATE_LIMIT_PER_MINUTE requests in the last 60s."""
    now = time.time()
    window_start = now - 60.0

    # Clean old entries
    _rate_limit_store[client_ip] = [
        ts for ts in _rate_limit_store[client_ip] if ts > window_start
    ]

    if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_PER_MINUTE:
        return True

    # Record this request
    _rate_limit_store[client_ip].append(now)
    return False


def _get_client_ip(request: Request) -> str:
    """Extract client IP, respecting proxy headers."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# --- Global Concurrency Semaphore ---
_semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)


def _is_heavy_request(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in HEAVY_PREFIXES)


@app.middleware("http")
async def protection_middleware(request: Request, call_next):
    """Combined rate limiting + concurrency control for heavy endpoints."""
    path = request.url.path

    if not _is_heavy_request(path):
        return await call_next(request)

    # 1. Check per-IP rate limit
    client_ip = _get_client_ip(request)
    if _is_rate_limited(client_ip):
        return JSONResponse(
            status_code=429,
            content={
                "detail": (
                    f"Rate limit exceeded ({RATE_LIMIT_PER_MINUTE}/minute per IP). "
                    "Please slow down your requests."
                )
            },
        )

    # 2. Check global concurrency
    if _semaphore.locked():
        return JSONResponse(
            status_code=429,
            content={
                "detail": (
                    f"Server is at max capacity ({MAX_CONCURRENT_TASKS} concurrent tasks). "
                    "Please wait and retry, or use the /async endpoints."
                )
            },
        )

    async with _semaphore:
        response = await call_next(request)
        return response


# --- Root redirect for HF Spaces health check ---
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to Gradio UI (also serves as HF Spaces health check)."""
    return RedirectResponse(url="/ui/")
