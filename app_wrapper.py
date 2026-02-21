"""Wrapper to add health-check, rate limiting, and concurrency control for HF Spaces."""

import asyncio
import os

from docling_serve.app import create_app
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse, RedirectResponse

# --- Configuration ---
RATE_LIMIT = os.environ.get("DOCLING_WRAPPER_RATE_LIMIT", "2/minute")
MAX_CONCURRENT_TASKS = int(os.environ.get("DOCLING_WRAPPER_MAX_CONCURRENT", "3"))

# Heavy endpoint prefixes that need protection
HEAVY_PREFIXES = ("/v1/convert", "/v1/chunk")

# --- App Setup ---
limiter = Limiter(key_func=get_remote_address, default_limits=[])
app = create_app()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Global Concurrency Semaphore ---
_semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)


@app.middleware("http")
async def concurrency_limit_middleware(request: Request, call_next):
    """Reject heavy requests when the server is already at max capacity."""
    path = request.url.path

    if any(path.startswith(prefix) for prefix in HEAVY_PREFIXES):
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

    return await call_next(request)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply per-IP rate limiting to heavy conversion/chunking endpoints."""
    path = request.url.path

    if any(path.startswith(prefix) for prefix in HEAVY_PREFIXES):
        try:
            await limiter._check_request_limit(request, None, [RATE_LIMIT])
        except Exception:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        f"Rate limit exceeded ({RATE_LIMIT} per IP). "
                        "Please slow down your requests."
                    )
                },
            )

    response = await call_next(request)
    return response


# --- Root redirect for HF Spaces health check ---
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to Gradio UI (also serves as HF Spaces health check)."""
    return RedirectResponse(url="/ui/")
