# Optional Dependencies

Before installing any extras we assume you have already:

1. **Cloned the repository**

   ```bash
   git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
   cd Insight_Ingenious
   ```
2. **Installed [uv](https://github.com/astral-sh/uv)** (one‑liner):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

With those prerequisites in place, the *core* Insight Ingenious framework installs with:

```bash
uv pip install -e .
```

Some features live in *extras* you can add **after** cloning the repo.

## Dataprep crawler (Scrapfly)

```bash
# crawler only
uv pip install -e ".[dataprep]"

# crawler **plus** its unit & e2e test suite
uv pip install -e ".[dataprep,tests]"
```

Use the second command if you plan to run `pytest` for the dataprep code—the extra `tests` group pulls in **pytest**, fixtures, and live‑network helpers.

All usage instructions live in:

```
docs/optional_dependencies/dataprep/README.md
```

### Document‑processing subsystem

The *document‑processing* extra bundles lightweight extractors for PDF, DOCX, PPTX and plain‑text sources, together with a Typer‑based CLI for batch extraction.

```bash
# core engines (PyMuPDF and Azure AI Document Intelligence wrapper)
uv pip install -e ".[document-processing]"

# add optional engines and the test‑suite
uv pip install -e ".[document-processing,pdfminer,unstructured,tests]"
```

| Extra name            | Purpose                                       | Extra packages pulled in                   |
| --------------------- | --------------------------------------------- | ------------------------------------------ |
| `document-processing` | PyMuPDF extractor, Azure DI client & CLI glue | `pymupdf`, `azure-ai-documentintelligence` |
| `pdfminer`            | Pure‑Python PDF extractor (no native libs)    | `pdfminer.six`                             |
| `unstructured`        | DOCX / PPTX / rich‑text extractor             | `unstructured[all-docs]`                   |

Full usage details are provided in:

```
docs/optional_dependencies/document_processing/README.md
```
