FROM ghcr.io/docling-project/docling-serve:latest

ENV DOCLING_SERVE_ENABLE_UI=true \
    UVICORN_PORT=7860 \
    UVICORN_HOST=0.0.0.0 \
    DOCLING_SERVE_MAX_SYNC_WAIT=300 \
    PYTHONWARNINGS="ignore::UserWarning"

# Download the SmolVLM model required by the UI for Picture Description
RUN docling-tools models download-hf-repo HuggingFaceTB/SmolVLM-256M-Instruct

# Install slowapi for IP-based rate limiting (not included in docling-serve)
RUN pip install --no-cache-dir slowapi

# Add wrapper that provides a root "/" endpoint, rate limiting, and concurrency control
COPY --chown=1001:0 app_wrapper.py /opt/app-root/src/app_wrapper.py

# HF Spaces expects port 7860
EXPOSE 7860

CMD ["uvicorn", "app_wrapper:app"]
