"""Wrapper to add a root health-check endpoint for HF Spaces."""

from docling_serve.app import create_app
from starlette.responses import RedirectResponse

app = create_app()


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API docs (also serves as HF Spaces health check)."""
    return RedirectResponse(url="/docs")
