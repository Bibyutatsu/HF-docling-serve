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

# Docling Serve on Hugging Face Spaces

Running [Docling](https://github.com/docling-project/docling) as an API service, powered by [docling-serve](https://github.com/docling-project/docling-serve).

## Endpoints

- **API**: `/v1/convert/source`
- **UI Playground**: `/ui`
- **API Docs**: `/docs`

## Usage

```bash
curl -X POST "https://Bibyutatsu-AzureDocling-serve.hf.space/v1/convert/source" \
  -H "Content-Type: application/json" \
  -d '{"sources": [{"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}]}'
```
