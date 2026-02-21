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

# 📄 Docling Serve on Hugging Face Spaces

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/Bibyutatsu/HF-docling-serve)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A free, hosted, API-ready instance of [docling-serve](https://github.com/docling-project/docling-serve) (by IBM) running on Hugging Face Spaces. Convert PDFs, DOCX, PPTX, HTML, images, and more into structured formats (Markdown, JSON, text) using AI-powered document understanding.

**Perfect for quick testing, hackathons, and small RAG pipelines without the hassle of setting up local heavyweight ML models.**

---

## 🚀 Live Instance

| Interface | URL |
|---|---|
| **🎮 Gradio UI (Demo)** | [huggingface.co/spaces/Bibyutatsu/HF-docling-serve](https://Bibyutatsu-HF-docling-serve.hf.space/ui) |
| **📖 OpenAPI Docs (Swagger)** | [Bibyutatsu-HF-docling-serve.hf.space/docs](https://Bibyutatsu-HF-docling-serve.hf.space/docs) |
| **📐 Scalar API Docs** | [Bibyutatsu-HF-docling-serve.hf.space/scalar](https://Bibyutatsu-HF-docling-serve.hf.space/scalar) |

> ⚠️ **Important Note on Cold Starts**: Since this runs on the free Hugging Face Spaces tier, the environment goes to sleep after ~48h of inactivity. The **first request** after sleep takes **~2–5 minutes** to cold-start (due to loading PyTorch models and checking dependencies). Subsequent requests are very fast.

### ⚡ Fair-Use Rate Limits

To keep this free instance stable for everyone, the following limits are enforced:

| Limit | Value |
|---|---|
| **Per-IP Rate Limit** | 2 requests / minute on `/v1/convert/*` and `/v1/chunk/*` |
| **Global Concurrency** | Max 3 simultaneous heavy processing tasks |

If you hit these limits you'll receive a `429 Too Many Requests` response. Use the **async endpoints** (`/v1/convert/source/async`) for heavy workloads — they queue efficiently.

---

## 📚 What It Does

This space utilizes IBM's [Docling](https://github.com/docling-project/docling) ML models under the hood, offering:

- **Advanced Layout Detection:** Identifies text blocks, tables, figures, headers, etc.
- **Table Structure Recognition:** Extracts complex tables into structured tabular formats.
- **Robust OCR:** Uses RapidOCR and EasyOCR for scanned documents and images.
- **VLM Features:** Picture classification to automatically identify and describe images within documents.

### Supported Formats
- **Input:** PDF, DOCX, PPTX, XLSX, HTML, Markdown, AsciiDoc, CSV, Images (PNG, JPEG, TIFF, BMP, GIF)
- **Output:** Markdown, JSON (Docling Document format), Text, Doctags

---

## 🔌 API Reference & Usage Notes

Base URL for all API requests:  
📝 `https://Bibyutatsu-HF-docling-serve.hf.space`

### 1. Document Conversion (Synchronous)

Wait for completion and get the parsed result immediately. Best for smaller files.

**From URL:**
```bash
curl -X POST "https://Bibyutatsu-HF-docling-serve.hf.space/v1/convert/source" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [{"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}]
  }'
```

**From File Upload:**
```bash
curl -X POST "https://Bibyutatsu-HF-docling-serve.hf.space/v1/convert/file" \
  -F "files=@/path/to/document.pdf"
```

### 2. Document Conversion (Asynchronous)

Start a conversion task and receive a `task_id` immediately. Recommended for large or complex documents to avoid HTTP timeouts.

**From URL:**
```bash
curl -X POST "https://Bibyutatsu-HF-docling-serve.hf.space/v1/convert/source/async" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [{"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}]
  }'
```

**Manage Async Tasks:**
```bash
# Check task status (Wait for "status": "completed")
curl "https://Bibyutatsu-HF-docling-serve.hf.space/v1/task/{task_id}/status"

# Fetch final parsing result
curl "https://Bibyutatsu-HF-docling-serve.hf.space/v1/task/{task_id}/result"
```

### 3. Document Chunking for RAG

Docling-Serve provides specialized chunking endpoints for vector databases.

**Hybrid Chunker:**
```bash
curl -X POST "https://Bibyutatsu-HF-docling-serve.hf.space/v1/chunk/hybrid/source" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [{"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}]
  }'
```

*Note: All endpoints have corresponding `/file` and `/async` variants.*

---

## 🐍 Python Example

A quick script to parse a document from an external URL in Python:

```python
import requests
import time
import zipfile
import io

BASE_URL = "https://Bibyutatsu-HF-docling-serve.hf.space"

# --- Example 1: Async Conversion (Recommended for Large PDFs to avoid 504 Timeouts) ---
print("Task 1: Starting Async Conversion for a single document...")
response_async = requests.post(
    f"{BASE_URL}/v1/convert/source/async",
    json={"sources": [{"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}]}
)

if response_async.status_code == 200:
    task_id = response_async.json().get("task_id")
    print(f"Task started with ID: {task_id}. Polling for completion...")
    
    status = "pending"
    while status in ["pending", "processing"]:
        time.sleep(5) # Wait 5 seconds before checking again
        res = requests.get(f"{BASE_URL}/v1/task/{task_id}/status")
        status = res.json().get("status")
        print(f"Current status: {status}")
        
    if status == "completed":
        result_res = requests.get(f"{BASE_URL}/v1/task/{task_id}/result")
        result = result_res.json()
        print("Async Conversion Successful!")
        print(result['document']['md_content'][:200] + "...\n")
    else:
        print("Task failed or was cancelled.")
else:
    print(f"Error starting async task: {response_async.status_code}", response_async.text)


# --- Example 2: Convert Multiple Documents (Returns a ZIP file) ---
# Note: Can also be done asynchronously via /v1/convert/source/async with multiple sources!
print("Task 2: Converting multiple documents (Synchronous)...")
response_multi = requests.post(
    f"{BASE_URL}/v1/convert/source",
    json={
        "sources": [
            {"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"},
            {"kind": "http", "url": "https://arxiv.org/pdf/1706.03762"}
        ]
    }
)

if response_multi.status_code == 200:
    content_type = response_multi.headers.get("Content-Type")
    if content_type == "application/zip":
        print("Multiple Document Conversion Successful! Received ZIP file.")
        # Extract the ZIP in memory
        with zipfile.ZipFile(io.BytesIO(response_multi.content)) as z:
            print("Files in ZIP:", z.namelist())
    else:
        print(f"Expected ZIP, received: {content_type}")
else:
    print(f"Error (Sync Multi): {response_multi.status_code}", response_multi.text)
```

---

## 🏗️ Architecture

This repository deploys the official [`ghcr.io/docling-project/docling-serve`](https://github.com/docling-project/docling-serve/pkgs/container/docling-serve) Docker image to [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker) with a minimal custom wrapper for health-check compliance.

```
┌──────────────────────────────────────┐
│  Hugging Face Spaces (Free Tier)     │
│  2 vCPU · 16 GB RAM · CPU Basic      │
├──────────────────────────────────────┤
│  Custom Dockerfile                   │
│  ├── FROM docling-serve:latest       │
│  ├── app_wrapper.py                  │
│  │   ├── Root "/" → "/ui/" redirect  │
│  │   ├── slowapi rate limiter        │
│  │   └── Concurrency semaphore       │
│  └── Exposes Port: 7860              │
├──────────────────────────────────────┤
│  docling-serve (FastAPI + Uvicorn)   │
│  ├── Layout detection model          │
│  ├── Table structure model           │
│  └── OCR / Picture classifier        │
└──────────────────────────────────────┘
```

**Why a custom wrapper?**  
HF Spaces health checks require a response at `/`. The wrapper also adds per-IP rate limiting (via `slowapi`) and a global concurrency semaphore to prevent memory exhaustion on the free tier.

---

## 🤝 Community & Acknowledgements

This Space is highly indebted to the team at **IBM** for pushing forward the open-source document understanding ecosystem. 

For core Docling issues, feature requests, or local deployment, please refer to the official repositories:
- [docling-project/docling-serve](https://github.com/docling-project/docling-serve)
- [docling-project/docling](https://github.com/docling-project/docling)

---

## 📝 License

This specific Hugging Face Space wrapper repository is licensed under the [MIT License](LICENSE).
Docling and its derivatives retain their respective original licenses.
