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
