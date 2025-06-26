## Document‑processing Optional Dependency

The *document‑processing* extra equips Insight Ingenious with a unified API and CLI for turning **born‑digital** documents into structured text blocks.
It is ideal for:

* RAG pipelines that need paragraph‑level text with coordinates
* Data‑prep flows that must normalise mixed PDF + DOCX + PPTX collections
* Quickly inspecting files from the command line without writing Python

---

### 1  Installation

```bash
# minimal feature set (PyMuPDF + Azure Document Intelligence wrapper + CLI)
uv pip install -e ".[document-processing]"

# include pure‑Python PDFMiner and rich‑text Unstructured engines
uv pip install -e ".[document-processing,pdfminer,unstructured]"
```

> **Why separate extras?**
>
> * *PyMuPDF* is the fastest path for standard PDFs.
> * *PDFMiner* avoids native code – useful on Alpine or AWS Lambda.
> * *Unstructured* adds DOCX, PPTX, HTML and exotic formats.

---

### 2  Command‑line quick‑start

```bash
# 1️⃣  Stream a remote PDF through pdfminer engine
ingen document-processing https://example.com/contract.pdf --engine pdfminer --out pages_pdfminer.jsonl
```

---

### 3  Python API in three lines

```python
from pathlib import Path
from ingenious.document_processing import extract

elements = list(extract(Path("report.pdf")))  # defaults to PyMuPDF
print(elements[0]["text"])
```

#### Choosing a specific engine

```python
for block in extract("paper.pdf", engine="pdfminer"):
    ...
```

Valid `engine` values (all case‑sensitive):

| Engine key     | Dependency (extra)    | Best for                                   |
| -------------- | --------------------- | ------------------------------------------ |
| `pymupdf`      | `document-processing` | Fast positional PDF extraction             |
| `pdfminer`     | `pdfminer`            | Pure‑Python / Alpine / Lambda builds       |
| `unstructured` | `unstructured`        | DOCX, PPTX, HTML, TXT, unusual PDFs        |
| `azdocint`     | `document-processing` | Cloud‑based Azure AI Document Intelligence |

---

### 4  Azure AI Document Intelligence engine

Cloud extraction unlocks semantic paragraphs and table metadata. Set two environment variables before running or importing:

```bash
export AZURE_DOC_INTEL_ENDPOINT="https://<resource>.cognitiveservices.azure.com"
export AZURE_DOC_INTEL_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

The service is pay‑as‑you‑go; the tiny unit tests stay within the free tier.

---

### 5  Streaming vs list

Every extractor yields **lazy** generators. Consume them as you like:

```python
# memory‑efficient streaming
for element in extract("big.pdf"):
    process(element)

# materialise everything (convenient, but RAM‑heavy)
all_blocks = list(extract("big.pdf"))
```

---

### 6  Running the test‑suite

#### Azure Document Intelligence integration assets

The Azure DI tests look for four tiny sample files –

* `sample.pdf`
* `sample.jpg`
* `sample.png`
* `sample.tiff`

– inside `ingenious/document_processing/tests/data_azure_doc_intell/`.
Create that folder and drop the files in before running `pytest -m integration`.
If the folder or any file is missing, the tests are auto-skipped, so the rest of the suite still runs cleanly.

```bash
# core engines only
uv pip install -e ".[document-processing,tests]"

uv run pytest
```

Add `pdfminer` and `unstructured` extras to expand coverage:

```bash
uv pip install -e ".[document-processing,pdfminer,unstructured,tests]"
```

---

### 7  Troubleshooting

| Symptom                                  | Likely cause / fix                                    |
| ---------------------------------------- | ----------------------------------------------------- |
| `ValueError: Unknown engine 'xyz'`       | Typo — run `ingen document-processing extract --help` |
| `ModuleNotFoundError: fitz`              | Forgot `document-processing` extra                    |
| CLI exits with *extra not installed* tip | Install the suggested extra with `uv pip install`     |
| Empty output on scanned PDF              | Engine has no OCR — use Azure DI                      |

---

Happy extracting 📑
