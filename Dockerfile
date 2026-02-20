FROM ghcr.io/docling-project/docling-serve:latest

ENV DOCLING_SERVE_ENABLE_UI=true

# HF Spaces expects port 7860
EXPOSE 7860

CMD ["docling-serve", "run", "--host", "0.0.0.0", "--port", "7860"]
