# Ingenious Development Workspace

This workspace is dedicated to the iterative development, integration, and testing of the **ingenious** framework as a production-ready Python library.

## Quick Start

1. **Start mock Azure services:**
   ```bash
   ../mock-azure-services.sh start
   ```

2. **Sync workspace dependencies:**
   ```bash
   uv sync
   ```

3. **Run basic functionality tests:**
   ```bash
   ./test-runner.sh basic
   ```

4. **Run Prompt Ensemble Agent tests:**
   ```bash
   ./test-runner.sh ensemble
   ```

5. **Run Azure integration tests:**
   ```bash
   ./test-runner.sh azure
   ```

## Testing Philosophy

This workspace uses **NO pytest**. All testing is done using:
- `uv run python -c "..."` commands
- Shell (bash) scripts
- Direct Python execution

## Mock Services

The workspace tests against mocked Azure APIs:
- **Azure OpenAI** - Port 5001
- **Azure Blob Storage** - Port 5002
- **Azure Search** - Port 5003
- **Azure SQL** - Port 5004

## Development Scripts

- `test-runner.sh` - Main test runner with different test suites
- `demo-ensemble.py` - Interactive demo of Prompt Ensemble Agent
- `validate-azure.py` - Validate Azure service integrations
- `benchmark-performance.py` - Performance benchmarking
