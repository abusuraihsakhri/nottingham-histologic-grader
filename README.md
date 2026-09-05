# Nottingham Histologic Grader

> **Domain:** Digital Pathology & Quantitative Histopathology
> **Reference Guidelines & Standards:** `College of American Pathologists (CAP) Synoptic Protocols & DICOM WSI`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## What It Does

Nottingham Histologic Score for Breast Carcinoma. Calculates Elston-Ellis Nottingham grade (1, 2, 3) from tubule formation, nuclear pleomorphism, and mitoses.

Zero-dependency Python implementation with single and batch evaluation.

Author: Dr. Abu Suraih Sakhri
License: MIT

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/nottingham-histologic-grader.git
cd nottingham-histologic-grader

# Install dependencies (FastAPI, uvicorn, pydantic, pytest)
pip install fastapi uvicorn pydantic pytest
```

---

## Key Capabilities & Algorithmic Modules

### Analytical Functions

- **`calculate_metrics()`**: Core domain algorithm that computes a weighted score from numeric inputs and classifies into risk tiers.
- **`process_single()`**: Evaluates a single case from CLI arguments.
- **`process_batch()`**: Processes a CSV file of cases, appending score/classification/recommendation columns.

---

## CLI Quickstart & Usage

### 1. Single Case Evaluation
```bash
python nottingham_grader.py single --v1 14.5 --v2 4.2 --v3 1.8
```

### 2. Batch CSV Processing
```bash
python nottingham_grader.py batch -i sample.csv -o results.csv
```

### 3. Enterprise CLI (with audit trail)
```bash
# Run single task evaluation
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2

# Batch process CSV records
python cli.py batch -i sample.csv -o results.csv

# Verify HMAC audit trail integrity
python cli.py verify-audit

# Launch FastAPI REST server
python cli.py serve --host 127.0.0.1 --port 8000
```

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Unique patient identifier | Required |
| `v1` | Tubule formation score (1-3) | Required |
| `v2` | Nuclear pleomorphism score (1-3) | Required |
| `v3` | Mitotic count score (1-3) | Required |

---

## Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Secure Secret Management:** Audit signing key resolved from `AUDIT_SECRET_KEY` environment variable; generates a cryptographically secure random key if not set (with warning).
* **Input Validation:** All numeric inputs validated for finiteness and safe magnitude bounds.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `AUDIT_SECRET_KEY` | Secret key for HMAC-SHA256 audit trail signing | Randomly generated (session-only) |
| `MODEL_PROVIDER` | LLM provider for chat/audit (`mock`, `ollama`, `claude`, `openai`) | `mock` |

---

## Testing & Verification

Run the full automated test suite:

```bash
pytest -v
```

Run with coverage:

```bash
pytest -v --tb=short
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## Container Deployment

```bash
docker build -t nottingham-histologic-grader .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key nottingham-histologic-grader
```

Or using Docker Compose:

```bash
docker-compose up -d
```

---

## Project Structure

```
nottingham-histologic-grader/
├── nottingham_grader.py     # Core grading algorithm & CLI
├── cli.py                   # Enterprise CLI with audit trail
├── simulator.py             # High-throughput stress testing
├── enrichment.py            # Enrichment feature engines
├── sample.csv               # Sample input data
├── benchmark_dataset.json   # Golden benchmark test cases
├── agents/
│   ├── __init__.py
│   ├── api.py               # FastAPI REST server
│   ├── base.py              # Security, PHI guard, audit trail
│   ├── models.py            # Pydantic data models
│   ├── supervisor.py        # Multi-worker orchestrator
│   ├── workers.py           # Specialized domain workers
│   ├── llm_factory.py       # LLM provider factory
│   ├── learning.py          # Bayesian calibration engine
│   ├── metrics.py           # Prometheus metrics exporter
│   └── streamer.py          # WebSocket telemetry broadcaster
├── tests/
│   ├── test_nottingham_histologic_grader.py
│   ├── test_enrichment.py
│   └── test_validation_and_security.py
├── Dockerfile
├── docker-compose.yml
└── openapi_spec.json
```
