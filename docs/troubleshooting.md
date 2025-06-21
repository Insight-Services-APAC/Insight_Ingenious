# Troubleshooting Guide

This guide helps you diagnose and resolve common issues when working with the Ingenious framework.

## Installation Issues

### Python Version Compatibility

**Problem:** `ERROR: Python 3.13 or higher is required`

**Solution:**
```bash
# Check current Python version
python --version

# Install Python 3.13+ using pyenv (recommended)
pyenv install 3.13.0
pyenv global 3.13.0

# Or using conda
conda install python=3.13

# Verify installation
python --version
```

### Package Installation Failures

**Problem:** `pip install insight-ingenious` fails

**Solutions:**

1. **Update pip:**
```bash
pip install --upgrade pip
```

2. **Use virtual environment:**
```bash
python -m venv ingenious-env
source ingenious-env/bin/activate  # Linux/Mac
# or
ingenious-env\Scripts\activate  # Windows
pip install insight-ingenious
```

3. **Install from source:**
```bash
git clone https://github.com/your-org/insight-ingenious.git
cd insight-ingenious
pip install -e .
```

### CLI Command Not Found

**Problem:** `ingen: command not found`

**Solutions:**

1. **Check PATH:**
```bash
# Find where pip installs scripts
python -m site --user-base
# Add {user-base}/bin to your PATH

# Temporarily add to PATH
export PATH="$(python -m site --user-base)/bin:$PATH"

# Permanently add to PATH (add to ~/.bashrc or ~/.zshrc)
echo 'export PATH="$(python -m site --user-base)/bin:$PATH"' >> ~/.bashrc
```

2. **Use module execution:**
```bash
python -m ingenious.cli --help
```

3. **Reinstall with --force-reinstall:**
```bash
pip install --force-reinstall insight-ingenious
```

## Configuration Issues

### Environment Variables Not Loaded

**Problem:** Configuration values are not being read from environment

**Solutions:**

1. **Check environment variables:**
```bash
# List all Ingenious-related variables
env | grep INGENIOUS
env | grep AZURE

# Set variables explicitly
export AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key"
```

2. **Use .env file:**
```bash
# Create .env file in project root
cat > .env << EOF
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_MODEL=gpt-4
EOF

# Load environment variables
python -c "from dotenv import load_dotenv; load_dotenv()"
```

3. **Validate configuration:**
```bash
# Check current configuration
ingen config show

# Validate configuration
ingen config validate
```

### Configuration File Not Found

**Problem:** `FileNotFoundError: config.yaml not found`

**Solutions:**

1. **Create configuration file:**
```bash
# Generate default configuration
ingen config init

# Or create manually
cat > config.yaml << EOF
application:
  name: "My Ingenious App"
  environment: "development"

azure:
  openai:
    endpoint: "https://your-endpoint.openai.azure.com"
    api_key: "your-api-key"
    model: "gpt-4"
EOF
```

2. **Specify configuration file path:**
```bash
# Use custom config file
ingen --config /path/to/config.yaml dev

# Set environment variable
export INGENIOUS_CONFIG_FILE="/path/to/config.yaml"
```

### Invalid Configuration Values

**Problem:** `ValidationError: Invalid configuration`

**Solution:**
```bash
# Get detailed validation errors
ingen config validate --verbose

# Check specific configuration section
python -c "
from ingenious.configuration.application.services import ConfigurationService
try:
    config = ConfigurationService.from_file('config.yaml')
    config.validate()
    print('✓ Configuration is valid')
except Exception as e:
    print(f'✗ Validation error: {e}')
"
```

## Azure Integration Issues

### Authentication Failures

**Problem:** `401 Unauthorized` or `403 Forbidden` errors

**Solutions:**

1. **Check API key:**
```bash
# Verify API key is set
echo $AZURE_OPENAI_API_KEY

# Test API key directly
curl -H "Authorization: Bearer $AZURE_OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     "$AZURE_OPENAI_ENDPOINT/openai/deployments/gpt-4/chat/completions?api-version=2024-06-01" \
     -d '{"messages":[{"role":"user","content":"test"}],"max_tokens":10}'
```

2. **Verify endpoint URL:**
```python
# Test connection
python -c "
from ingenious.external_integrations.infrastructure.openai_service import AzureOpenAIService
import asyncio

async def test():
    service = AzureOpenAIService(
        azure_endpoint='https://your-endpoint.openai.azure.com',
        api_key='your-api-key',
        api_version='2024-06-01',
        model='gpt-4'
    )
    try:
        response = await service.generate_response([
            {'role': 'user', 'content': 'Hello'}
        ])
        print('✓ Connection successful')
        print(f'Response: {response.content}')
    except Exception as e:
        print(f'✗ Connection failed: {e}')

asyncio.run(test())
"
```

3. **Check Azure RBAC permissions:**
```bash
# List your role assignments
az role assignment list --assignee $(az account show --query user.name -o tsv)

# Check specific resource permissions
az role assignment list --scope "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.CognitiveServices/accounts/{openai-resource}"
```

### Rate Limiting

**Problem:** `429 Too Many Requests` errors

**Solutions:**

1. **Implement exponential backoff:**
```python
import asyncio
import random

async def retry_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                delay = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited, retrying in {delay:.2f}s")
                await asyncio.sleep(delay)
            else:
                raise
```

2. **Reduce concurrent requests:**
```yaml
# In config.yaml
ensemble_defaults:
  max_concurrent_agents: 2  # Reduce from default 5
  timeout_seconds: 600      # Increase timeout
```

3. **Check quota limits:**
```bash
# Check current usage (if available)
az cognitiveservices account list-usage \
  --name your-openai-resource \
  --resource-group your-resource-group
```

### Storage Connection Issues

**Problem:** Azure Blob Storage connection failures

**Solutions:**

1. **Verify storage account URL:**
```python
# Test storage connection
python -c "
from ingenious.external_integrations.infrastructure.blob_storage_service import AzureBlobStorageService
import asyncio

async def test():
    service = AzureBlobStorageService(
        account_url='https://youraccount.blob.core.windows.net',
        credential='your-access-key'
    )
    try:
        # Test connection by listing containers
        containers = await service.list_containers()
        print('✓ Storage connection successful')
        print(f'Containers: {[c.name for c in containers]}')
    except Exception as e:
        print(f'✗ Storage connection failed: {e}')

asyncio.run(test())
"
```

2. **Check firewall settings:**
```bash
# Check storage account network rules
az storage account show \
  --name yourstorageaccount \
  --resource-group your-resource-group \
  --query networkRuleSet
```

3. **Verify container exists:**
```bash
# List containers
az storage container list \
  --account-name yourstorageaccount \
  --account-key your-access-key

# Create container if needed
az storage container create \
  --name ingenious-data \
  --account-name yourstorageaccount \
  --account-key your-access-key
```

## Ensemble Execution Issues

### Template Rendering Errors

**Problem:** `TemplateError: Variable 'x' is undefined`

**Solutions:**

1. **Check variable names:**
```python
# Debug template variables
template = "Analyze {{ topic }} focusing on {{ aspect }}"
variables = {"topic": "AI", "aspect": "ethics"}

from jinja2 import Template
try:
    rendered = Template(template).render(**variables)
    print(f"✓ Template rendered: {rendered}")
except Exception as e:
    print(f"✗ Template error: {e}")
```

2. **Provide default values:**
```jinja2
{# Use default values in templates #}
Analyze {{ topic | default("the given subject") }}
focusing on {{ aspect | default("general aspects") }}
```

3. **Validate variables before execution:**
```python
async def validate_ensemble_variables(config: EnsembleConfiguration, variables: dict):
    """Validate that all required variables are provided."""
    from jinja2 import Environment, meta

    env = Environment()

    # Check main prompt template
    ast = env.parse(config.main_prompt_template)
    required_vars = meta.find_undeclared_variables(ast)

    # Check sub-prompt templates
    for template in config.sub_prompt_templates:
        ast = env.parse(template.content)
        required_vars.update(meta.find_undeclared_variables(ast))

    # Check reduce template
    ast = env.parse(config.reduce_prompt_template)
    required_vars.update(meta.find_undeclared_variables(ast))

    missing_vars = required_vars - set(variables.keys())
    if missing_vars:
        raise ValueError(f"Missing required variables: {missing_vars}")
```

### Low Success Rate

**Problem:** Ensemble executions have low success rates

**Solutions:**

1. **Analyze failed agents:**
```python
async def analyze_failures(result: EnsembleResult):
    failed_agents = [exec for exec in result.agent_executions if not exec.is_successful]

    print(f"Failed agents: {len(failed_agents)}/{len(result.agent_executions)}")

    for execution in failed_agents:
        print(f"Agent {execution.agent_role}: {execution.error}")

    # Common failure patterns
    error_types = {}
    for execution in failed_agents:
        error_type = type(execution.error).__name__ if execution.error else "Unknown"
        error_types[error_type] = error_types.get(error_type, 0) + 1

    print(f"Error patterns: {error_types}")
```

2. **Adjust timeouts and retries:**
```yaml
# Increase timeouts for complex prompts
ensemble_defaults:
  timeout_seconds: 600  # 10 minutes
  retry_count: 5
```

3. **Simplify prompts:**
```python
# Break complex prompts into simpler ones
complex_prompt = "Analyze market, competitors, risks, opportunities, and create detailed recommendations"

# Better: Split into focused prompts
simple_prompts = [
    "Analyze the market size and trends for {{ product }}",
    "Identify top 3 competitors for {{ product }}",
    "List 3 key risks for {{ product }}",
    "Identify 3 key opportunities for {{ product }}"
]
```

### Performance Issues

**Problem:** Slow ensemble execution

**Solutions:**

1. **Use parallel strategy:**
```python
# Ensure independent prompts use parallel execution
config = await ensemble_use_case.create_ensemble_configuration(
    strategy="parallel",  # Not "sequential"
    max_concurrent_agents=5
)
```

2. **Optimize prompts for speed:**
```python
# ✓ Concise prompts
fast_prompt = "List 3 key benefits of {{ product }}. Be concise."

# ✗ Verbose prompts
slow_prompt = "Please provide a comprehensive and detailed analysis..."
```

3. **Monitor token usage:**
```python
async def monitor_token_usage(result: EnsembleResult):
    total_tokens = sum(exec.token_usage.get('total_tokens', 0)
                      for exec in result.agent_executions)

    print(f"Total tokens used: {total_tokens}")
    print(f"Average tokens per agent: {total_tokens / len(result.agent_executions)}")

    # Identify high token usage agents
    high_usage = [exec for exec in result.agent_executions
                  if exec.token_usage.get('total_tokens', 0) > 1000]

    if high_usage:
        print("High token usage agents:")
        for exec in high_usage:
            print(f"- {exec.agent_role}: {exec.token_usage.get('total_tokens')} tokens")
```

## Networking Issues

### Firewall and Proxy Issues

**Problem:** Connection timeouts or network errors

**Solutions:**

1. **Check network connectivity:**
```bash
# Test Azure OpenAI endpoint
curl -I https://your-endpoint.openai.azure.com

# Test Azure Storage
curl -I https://youraccount.blob.core.windows.net

# Check DNS resolution
nslookup your-endpoint.openai.azure.com
```

2. **Configure proxy settings:**
```bash
# Set proxy environment variables
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# Or in code
import os
os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
os.environ['HTTPS_PROXY'] = 'http://proxy.company.com:8080'
```

3. **Configure corporate firewall:**
```bash
# Azure OpenAI service endpoints to whitelist
# *.openai.azure.com
# *.blob.core.windows.net
# *.database.windows.net

# Check if specific ports are blocked
telnet your-endpoint.openai.azure.com 443
```

### SSL/TLS Issues

**Problem:** SSL certificate verification errors

**Solutions:**

1. **Update certificates:**
```bash
# Update system certificates (Ubuntu/Debian)
sudo apt-get update && sudo apt-get install ca-certificates

# Update certificates (CentOS/RHEL)
sudo yum update ca-certificates

# Update certificates (macOS)
brew install ca-certificates
```

2. **Verify SSL configuration:**
```python
import ssl
import socket

def check_ssl(hostname, port=443):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(f"✓ SSL connection to {hostname} successful")
            print(f"Protocol: {ssock.version()}")
            print(f"Cipher: {ssock.cipher()}")

# Test Azure endpoints
check_ssl("your-endpoint.openai.azure.com")
```

3. **Temporary SSL bypass (development only):**
```python
import ssl
import urllib3

# WARNING: Only for development/testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
```

## Development and Testing Issues

### Mock Services Not Working

**Problem:** Mock Azure services fail to start or respond

**Solutions:**

1. **Check mock service status:**
```bash
# Check if Prism is installed
npx @stoplight/prism-cli --version

# Start mock OpenAI service manually
npx @stoplight/prism-cli mock specs/azure-openai-transformed.json --port 5001

# Test mock service
curl http://localhost:5001/openai/deployments/gpt-4/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}]}'
```

2. **Regenerate transformed specs:**
```bash
# If specs are outdated, regenerate them
python transform-azure-spec.py \
  "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/AzureOpenAI/inference/stable/2024-06-01/inference.json" \
  specs/azure-openai-transformed.json
```

3. **Use alternative mock setup:**
```python
# Simple mock for testing
class MockOpenAIService:
    async def generate_response(self, messages, **kwargs):
        from openai.types.chat import ChatCompletionMessage
        return ChatCompletionMessage(
            role="assistant",
            content=f"Mock response for: {messages[-1]['content']}"
        )

# Use in tests
if os.getenv("TESTING"):
    openai_service = MockOpenAIService()
else:
    openai_service = AzureOpenAIService(...)
```

### Import Errors

**Problem:** `ImportError: No module named 'ingenious.xxx'`

**Solutions:**

1. **Check installation:**
```bash
# Verify package is installed
pip list | grep insight-ingenious

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Check if module exists
python -c "import ingenious; print(ingenious.__file__)"
```

2. **Reinstall in development mode:**
```bash
# If working with source code
pip install -e .

# Or full reinstall
pip uninstall insight-ingenious
pip install insight-ingenious
```

3. **Check for name conflicts:**
```bash
# Look for conflicting packages
pip list | grep -i ingenious

# Check for local files that might conflict
find . -name "ingenious*" -type f
```

## Logging and Debugging

### Enable Debug Logging

**Problem:** Need more detailed error information

**Solution:**
```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable specific logger
logger = logging.getLogger('ingenious')
logger.setLevel(logging.DEBUG)

# Or via environment variable
import os
os.environ['INGENIOUS_DEBUG'] = 'true'
os.environ['INGENIOUS_LOG_LEVEL'] = 'DEBUG'
```

### Trace Execution

**Problem:** Need to understand execution flow

**Solution:**
```python
import traceback
import sys

def trace_calls(frame, event, arg):
    if event == 'call' and 'ingenious' in frame.f_code.co_filename:
        print(f"Calling: {frame.f_code.co_filename}:{frame.f_lineno} {frame.f_code.co_name}")
    return trace_calls

# Enable tracing
sys.settrace(trace_calls)

# Or use logging
import structlog

logger = structlog.get_logger()

async def traced_execution():
    logger.info("Starting ensemble execution")
    try:
        result = await ensemble_use_case.execute_ensemble(config_id, variables)
        logger.info("Ensemble execution completed", success_rate=result.success_rate)
        return result
    except Exception as e:
        logger.error("Ensemble execution failed", error=str(e), traceback=traceback.format_exc())
        raise
```

## Getting Help

### Community Resources

1. **GitHub Issues:** Report bugs and feature requests
2. **Documentation:** Check the latest documentation
3. **Examples:** Review example implementations
4. **Stack Overflow:** Search for `ingenious-framework` tag

### Diagnostic Information

When reporting issues, include:

```bash
# System information
python --version
pip --version
uname -a

# Package information
pip list | grep -E "(ingenious|azure|openai)"

# Configuration (remove sensitive data)
ingen config show --format yaml

# Error logs
tail -n 50 ~/.ingenious/logs/error.log

# Health check
ingen health --verbose
```

### Emergency Troubleshooting

If all else fails:

```bash
# Nuclear option: Fresh installation
pip uninstall insight-ingenious
pip cache purge
python -m venv fresh-env
source fresh-env/bin/activate
pip install --upgrade pip
pip install insight-ingenious

# Test basic functionality
python -c "import ingenious; print('Import successful')"
ingen --help
```

Remember: Most issues are configuration-related. Double-check your Azure credentials, endpoint URLs, and network connectivity before diving into code-level debugging.
