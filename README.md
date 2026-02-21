---
title: Docling Serve
emoji: 📄
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 📄 Docling Serve — Document Conversion API

> A free, hosted instance of [docling-serve](https://github.com/docling-project/docling-serve) (by IBM) running on Hugging Face Spaces. Convert PDFs, DOCX, PPTX, HTML, images, and more into structured formats (Markdown, JSON, text) using AI-powered document understanding.

## 🚀 Live Instance

| | URL |
|---|---|
| **🎮 Demo UI** | [huggingface.co/spaces/Bibyutatsu/AzureDocling-serve](https://Bibyutatsu-AzureDocling-serve.hf.space/ui) |
| **📖 API Docs** | [Bibyutatsu-AzureDocling-serve.hf.space/docs](https://Bibyutatsu-AzureDocling-serve.hf.space/docs) |
| **📐 Scalar Docs** | [Bibyutatsu-AzureDocling-serve.hf.space/scalar](https://Bibyutatsu-AzureDocling-serve.hf.space/scalar) |

> **Note**: The Space sleeps after ~48h of inactivity. The first request after sleep takes ~2–5 min to cold-start (ML models loading). Subsequent requests are fast.

---

## 📚 What It Does

Docling Serve uses IBM's [Docling](https://github.com/docling-project/docling) engine under the hood, which includes:

- **Layout Detection** — AI model that identifies text blocks, tables, figures, headers, etc.
- **Table Structure Recognition** — Extracts tables into structured data
- **OCR** (RapidOCR + EasyOCR) — Handles scanned documents and images
- **Picture Classification** — Identifies and describes images in documents

### Supported Input Formats
PDF, DOCX, PPTX, XLSX, HTML, Markdown, AsciiDoc, CSV, Images (PNG, JPEG, TIFF, BMP, GIF)

### Supported Output Formats
Markdown, JSON (Docling Document format), Text, Doctags

---

## 🔌 API Reference

Base URL: `https://Bibyutatsu-AzureDocling-serve.hf.space`

### Document Conversion

#### Convert from URL (Synchronous)
Convert documents by providing URLs. Waits for completion and returns the result.

```bash
curl -X POST "https://Bibyutatsu-AzureDocling-serve.hf.space/v1/convert/source" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}
    ]
  }'
```

#### Convert from File Upload (Synchronous)
Upload a local file for conversion.

```bash
curl -X POST "https://Bibyutatsu-AzureDocling-serve.hf.space/v1/convert/file" \
  -F "files=@/path/to/document.pdf"
```

#### Convert from URL (Async)
Start a conversion task and get a task ID back immediately.

```bash
curl -X POST "https://Bibyutatsu-AzureDocling-serve.hf.space/v1/convert/source/async" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}
    ]
  }'
```

#### Convert from File Upload (Async)

```bash
curl -X POST "https://Bibyutatsu-AzureDocling-serve.hf.space/v1/convert/file/async" \
  -F "files=@/path/to/document.pdf"
```

### Document Chunking

Split documents into chunks for use in RAG pipelines:

#### Hybrid Chunker (from URL)

```bash
curl -X POST "https://Bibyutatsu-AzureDocling-serve.hf.space/v1/chunk/hybrid/source" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}
    ]
  }'
```

#### Hierarchical Chunker (from URL)

```bash
curl -X POST "https://Bibyutatsu-AzureDocling-serve.hf.space/v1/chunk/hierarchical/source" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}
    ]
  }'
```

> All chunking endpoints also support `/file` and `/async` variants (e.g., `/v1/chunk/hybrid/file/async`).

### Task Management (for Async APIs)

```bash
# Check task status
curl "https://Bibyutatsu-AzureDocling-serve.hf.space/v1/task/{task_id}/status"

# Get task result
curl "https://Bibyutatsu-AzureDocling-serve.hf.space/v1/task/{task_id}/result"
```

### Health & Info

```bash
# Version info
curl "https://Bibyutatsu-AzureDocling-serve.hf.space/version"
```

---

## 🐍 Python Usage

```python
import requests

BASE_URL = "https://Bibyutatsu-AzureDocling-serve.hf.space"

# Convert a PDF from URL
response = requests.post(
    f"{BASE_URL}/v1/convert/source",
    json={
        "sources": [
            {"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}
        ]
    }
)
result = response.json()
print(result)

# Upload a local file
with open("document.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/v1/convert/file",
        files={"files": f}
    )
    result = response.json()
    print(result)
```

---

## 🏗️ Architecture

This repo deploys the official [`ghcr.io/docling-project/docling-serve`](https://github.com/docling-project/docling-serve/pkgs/container/docling-serve) Docker image to [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker) with a thin wrapper:

```
┌────────────────────────────────────┐
│  Hugging Face Spaces (Free Tier)   │
│  2 vCPU · 16 GB RAM · CPU Basic   │
├────────────────────────────────────┤
│  Dockerfile                        │
│  └── FROM docling-serve:latest     │
│  └── app_wrapper.py (root "/" fix) │
│  └── Port: 7860                    │
├────────────────────────────────────┤
│  docling-serve (FastAPI + Uvicorn) │
│  ├── Layout detection model        │
│  ├── Table structure model         │
│  ├── RapidOCR + EasyOCR            │
│  └── Picture classifier            │
└────────────────────────────────────┘
```

### Files

| File | Purpose |
|---|---|
| `Dockerfile` | Extends the official docling-serve image, overrides port to 7860 |
| `app_wrapper.py` | Adds a `GET /` redirect to `/ui` (required by HF Spaces health checks) |
| `README.md` | HF Spaces config (YAML front matter) + this documentation |

---

## 🔄 Sync Setup

This repo pushes to **both** GitHub and Hugging Face Spaces:

```bash
# GitHub (source of truth)
git remote -v
# origin  https://github.com/Bibyutatsu/AzureDocling-serve.git

# HF Spaces (deployment)
# hf      https://huggingface.co/spaces/Bibyutatsu/AzureDocling-serve

# Push to both
git push origin main
git push hf main
```

---

## 📝 License

MIT — see [LICENSE](LICENSE).

Built on top of [docling-serve](https://github.com/docling-project/docling-serve) by IBM.
