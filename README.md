# Nottingham Histologic Grader

A small, deterministic calculator for the **Nottingham (Elston–Ellis) combined histologic grade** of invasive breast carcinoma. It takes three **already assigned component scores**, not slide images or uncalibrated raw mitotic counts.

## Use the browser calculator

Open [web/index.html](web/index.html) locally in a modern browser. All grade calculation, CSV parsing and export run in JavaScript on the device. No Python, server, API keys, uploads or external packages are required.

A GitHub Pages publishing workflow is included; the live URL should only be advertised after Pages has been enabled and the deployment has been verified.

## Grading method

| Component | Score |
| --- | --- |
| Tubule / gland formation | 1 for >75%; 2 for 10–75%; 3 for <10% |
| Nuclear pleomorphism | 1 small/uniform; 2 moderately variable; 3 markedly pleomorphic |
| Mitotic activity | 1, 2 or 3 based on the **field-area-calibrated** mitotic scoring criteria |

Sum the components (range **3–9**): **Grade 1 = 3–5**, **Grade 2 = 6–7**, **Grade 3 = 8–9**. Mitotic thresholds vary with microscope field diameter, so this tool deliberately accepts the mitotic **component score**, not raw mitoses per high-power field.

References: [RCPA invasive breast cancer reporting](https://www.rcpa.edu.au/Library/Practising-Pathology/Structured-Pathology-Reporting-of-Cancer/Cancer-Protocols/Breast/Elements-invasive-breast) and [CAP invasive breast biopsy protocol (2026)](https://www.cap.org/wp-content/uploads/2026/06/Breast.Invasive.Bx_1.3.0.0.REL_CAPCP.pdf).

**Scope:** A calculation aid for qualified pathology users; it does not diagnose a specimen, grade images, stage cancer or recommend treatment.

## Batch CSV

Provide `v1,v2,v3` (tubules, nuclei, mitotic component) and optionally `case_id`. Download a sample from the browser interface or use [sample.csv](sample.csv). The browser accepts up to 5,000 rows and 2 MB per file. CSV exports are protected against spreadsheet formula injection.

## Python CLI

Python 3.10 or newer; no dependencies for the grading engine:

```bash
python nottingham_grader.py single --v1 1 --v2 2 --v3 3
python nottingham_grader.py batch -i sample.csv -o results.csv
```

Returns a total score, grade, classification and a reminder that histologic grade is not a treatment recommendation. Invalid or incomplete scores raise errors.

## Optional API and legacy demonstration tools

```bash
python -m pip install 'fastapi>=0.110,<1' 'uvicorn>=0.30,<1' 'pydantic>=2,<3'
python cli.py serve
```

The server opens at `http://127.0.0.1:8000/`. `POST /api/grade` accepts JSON `{"v1":1,"v2":2,"v3":3}`; `/docs` exposes generated API documentation. The separate `cli.py audit|chat|batch|verify-audit`, `/api/audit`, `/api/chat`, and `enrichment.py` are **legacy synthetic demonstrations** and must not be interpreted as clinically validated grading, decision support or actual LLM inference.

Docker is optional: export a **private persistent** `AUDIT_SECRET_KEY` before using `docker compose up --build`. See [.env.example](.env.example). Never commit a real key.

## Privacy and security

The browser calculator does not transmit or persist case input; repository links are only accessed when followed. Use de-identified case labels. The optional server receives whatever data its callers submit; the legacy regex-based identifier screen does **not** guarantee de-identification. Its audit chain is signed in memory only, not a durable compliance-grade audit log.

## Development and tests

```bash
python -m pip install pytest 'fastapi>=0.110,<1' 'uvicorn>=0.30,<1' 'pydantic>=2,<3' httpx
pytest -q
node --test tests/test_web.cjs
node --check web/app.js
```

CI tests Python 3.10–3.12 and Node 22. The browser UI uses standard HTML, CSS and JavaScript (modern browsers supporting `File.text()`). No Pyodide is necessary because the browser algorithm has a native JavaScript implementation.

## License

[MIT](LICENSE).
