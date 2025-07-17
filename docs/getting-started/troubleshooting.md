---
title: "Quick Troubleshooting"
layout: single
permalink: /getting-started/troubleshooting/
sidebar:
  nav: "docs"
toc: true
toc_label: "Quick Fixes"
toc_icon: "tools"
---

# 🆘 Troubleshooting Guide

Common issues and solutions when working with Insight Ingenious.

## 🔧 Configuration Issues

### Azure OpenAI Problems

**❌ Error: "Azure OpenAI API key not found"**

**Solution:**
1. Check your `profiles.yml` file:
   ```yaml
   - name: "dev"
     models:
       - model: "gpt-4.1-nano"
         api_key: "your-actual-api-key"  # ← Make sure this is set
         base_url: "https://your-endpoint.openai.azure.com/..."
   ```

2. Verify environment variables:
   ```bash
   echo $INGENIOUS_PROFILE_PATH
   # Should show: <pwd>/profiles.yml
   ```

3. Test configuration loading:
   ```bash
   uv run python -c "import ingenious.config.config as config; print(config.get_config().models[0].api_key)"
   ```

**❌ Error: "Invalid Azure OpenAI deployment"**

**Solution:**
- Ensure `config.yml` model name matches your Azure deployment name
- Verify API version is supported (use `2024-08-01-preview` or newer)
- Check your Azure OpenAI resource has the model deployed

### Environment Variables

**❌ Error: "Config file not found"**

**Solution:**
```bash
# Set correct paths
export INGENIOUS_PROJECT_PATH="$(pwd)/config.yml"
export INGENIOUS_PROFILE_PATH="$(pwd)/profiles.yml"

# Verify files exist
ls -la config.yml
ls -la profiles.yml
```

For Windows (PowerShell)
```powershell
# Set correct paths
$env:INGENIOUS_PROJECT_PATH="{project_path}/config.yml"
$env:INGENIOUS_PROFILE_PATH="{profile_path}/profiles.yml"

# Verify files exist
Get-ChildItem config.yml
Get-ChildItem profiles.yml
```

**❌ Error: "Permission denied accessing profiles.yml"**

**Solution:**
```bash
# Fix permissions
chmod 600 profiles.yml
```

## 🚀 Workflow Issues

### Workflow Not Available

**❌ Error: "conversation_flow not set" or "Unknown workflow"**

**Solution:**
1. Check available workflows:
   ```bash
   uv run ingen workflows
   ```

2. Use exact workflow names in API calls:
   ```bash
   # ✅ Correct
   curl -X POST http://localhost:80/api/v1/chat \
     -d '{"user_prompt": "Hello", "conversation_flow": "classification-agent"}'

   # ❌ Wrong
   curl -X POST http://localhost:80/api/v1/chat \
     -d '{"user_prompt": "Hello", "conversation_flow": "classify"}'
   ```

### Workflow Configuration Missing

**❌ Error: "Search service not configured"**

**Solution for `knowledge-base-agent` (Recommended - Local ChromaDB):**
No configuration needed! The knowledge-base-agent uses local ChromaDB by default.

1. Simply add documents to: `./.tmp/knowledge_base/`
2. Documents are automatically indexed in ChromaDB
3. Works immediately without external services

**Alternative: Azure Search (Experimental - May contain bugs):**
1. Add Azure Search to `config.yml`:
   ```yaml
   azure_search_services:
     - service: "default"
       endpoint: "https://your-search-service.search.windows.net"
   ```

2. Add API key to `profiles.yml`:
   ```yaml
   azure_search_services:
     - service: "default"
       key: "your-search-api-key"
   ```

**❌ Error: "Database connection failed"**

**Solution for `sql-manipulation-agent` (Recommended - Local SQLite):**
```yaml
# config.yml
azure_sql_services:
  database_name: "skip"  # This enables local mode
local_sql_db:
  database_path: "/tmp/sample_sql.db"
  sample_csv_path: "./data/your_data.csv"
```

**Alternative: Azure SQL (Experimental - May contain bugs):**
```yaml
# profiles.yml
azure_sql_services:
  database_connection_string: "Server=tcp:yourserver.database.windows.net,1433;Database=yourdatabase;..."
```

## 🌐 Server Issues

### Port Conflicts

**❌ Error: "Port already in use"**

**Solution:**
1. Find what's using the port:
  ```bash
  # On Linux/Mac
  lsof -i :8081

  # On Windows
  netstat -ano | findstr :8081
  ```

2. Kill the process or use a different port:
   ```bash
   # Use different port
   uv run ingen serve --port 8082
   ```

3. Or change the port in `config.yml`:
   ```yaml
   web_configuration:
     port: 8082
   ```

### Server Won't Start

**❌ Error: "FastAPI startup failed"**

**Solution:**
1. Check configuration syntax:
   ```bash
   # Test YAML syntax
   python -c "import yaml; yaml.safe_load(open('config.yml'))"
   ```

2. Check logs for specific errors
3. Start with minimal configuration first

## 📡 API Issues

### Authentication Problems

**❌ Error: "401 Unauthorized"**

**Solution:**
1. Check if authentication is enabled in `config.yml`:
   ```yaml
   web_configuration:
     authentication:
       enable: true  # ← If true, you need credentials
   ```

2. Use basic auth in requests:
   ```bash
   curl -X POST http://localhost:80/api/v1/chat \
     -H "Authorization: Basic $(echo -n username:password | base64)" \
     -d '{"user_prompt": "Hello", "conversation_flow": "classification-agent"}'
   ```

3. Or disable authentication for testing:
   ```yaml
   # profiles.yml
   web_configuration:
     authentication:
       enable: false
   ```

### Request Format Issues

**❌ Error: "422 Validation Error"**

**Solution:**
Ensure correct JSON format:
```bash
# ✅ Correct format
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Your message here",
    "conversation_flow": "classification-agent",
    "thread_id": "optional-thread-id"
  }'
```

Required fields:
- `user_prompt`: Your message (string)
- `conversation_flow`: Workflow name (string)

Optional fields:
- `thread_id`: For conversation continuity
- `topic`: Additional context

## 🧪 Testing & Debugging

### Check System Status

```bash
# 1. Check all workflow configurations
curl http://localhost:80/api/v1/workflows

# 2. Check specific workflow
curl http://localhost:80/api/v1/workflow-status/classification-agent

# 3. Check system diagnostics
curl http://localhost:80/api/v1/diagnostic
```

### Enable Debug Logging

```yaml
# config.yml
logging:
  root_log_level: debug
  log_level: debug
```

### Test Individual Components

```bash
# Test configuration loading
uv run python -c "import ingenious.config.config as config; print(config.get_config())"

# Test Azure OpenAI connection
uv run python -c "
from ingenious.dependencies import get_openai_service
service = get_openai_service()
print('OpenAI service created successfully')
"
```

## 📊 Performance Issues

### Slow Response Times

**Solutions:**
1. Check Azure OpenAI quota and rate limits
2. Use smaller models for testing
3. Reduce conversation complexity
4. Check network connectivity to Azure

### Memory Issues

**Solutions:**
1. Clear temporary files:
  ```bash
  # Linux/Mac
  rm -rf .tmp/*

  # Windows Command Prompt
  rmdir /s /q .tmp
  mkdir .tmp

  # Windows PowerShell
  Remove-Item -Recurse -Force .tmp\*
  ```

2. Restart the server periodically
3. Monitor memory usage

## 🔄 Common Workflow Fixes

### Start Fresh

If things are broken, reset to a clean state:

```bash
# 1. Stop the server (Ctrl+C)

# 2. Clear temporary files
rm -rf .tmp/

# 3. Verify configuration
uv run ingen workflows

# 4. Test minimal workflow first
uv run ingen serve
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Hello", "conversation_flow": "classification-agent"}'
```

### Progressive Setup

1. **Start simple**: Get `classification-agent` working first
2. **Add complexity**: Then try `knowledge-base-agent`
3. **Debug incrementally**: Don't configure everything at once

## 🆘 Getting Help

### Before Opening an Issue:

1. Check this troubleshooting guide
2. Review [Configuration Guide](../configuration/README.md)
3. Test with minimal configuration
4. Check GitHub issues for similar problems

### When Opening an Issue:

Include:
- Your `config.yml` (redact sensitive data)
- Error messages and logs
- Steps to reproduce
- Operating system and Python version
- Output of `uv run ingen workflows`

### Quick Diagnostic Info:

```bash
# Gather diagnostic info
echo "=== System Info ==="
uv --version
python --version

echo "=== Configuration Status ==="
uv run ingen workflows

echo "=== Workflow Status ==="
curl -s http://localhost:80/api/v1/workflows || echo "Server not running"
```

---

**🎯 Still stuck?** Join our community or open an issue on GitHub with the diagnostic information above.
