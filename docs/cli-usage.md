# CLI Usage Guide

The Ingenious CLI (`ingen`) provides powerful command-line tools for managing AI ensembles, running applications, and development workflows.

## Installation Verification

After installing Ingenious, verify the CLI is available:

```bash
ingen --help
```

## Core Commands

### Project Management

#### Initialize a New Project

```bash
# Create a new Ingenious project
ingen init my-project

# Initialize in current directory
ingen init .

# Specify project template
ingen init my-project --template advanced
```

This creates:
- Project structure with configuration files
- Example ensemble configurations
- Development environment setup

#### Development Server

```bash
# Start development server with auto-reload
ingen dev

# Specify port and host
ingen dev --host 0.0.0.0 --port 8080

# Enable debug mode
ingen dev --debug
```

#### Production Server

```bash
# Start production server
ingen run

# With custom configuration
ingen run --host 0.0.0.0 --port 8000 --workers 4

# Background process
ingen run --daemon
```

### Ensemble Management

The `ensemble` subcommand provides comprehensive ensemble management capabilities.

#### Create Ensemble Configurations

```bash
# Create from interactive prompts
ingen ensemble create my-analysis

# Create from configuration file
ingen ensemble create my-analysis --config config.json

# Specify execution strategy
ingen ensemble create my-analysis --strategy parallel --max-agents 3
```

Example configuration file (`config.json`):

```json
{
  "description": "Multi-perspective topic analysis",
  "main_prompt_template": "Analyze {{ topic }} comprehensively.",
  "sub_prompt_templates": [
    {
      "name": "strengths_analyzer",
      "content": "Analyze the strengths of {{ topic }}.",
      "role": "analyzer",
      "priority": 1
    },
    {
      "name": "challenges_critic",
      "content": "Identify challenges with {{ topic }}.",
      "role": "critic",
      "priority": 1
    }
  ],
  "reduce_prompt_template": "Synthesize the following analyses: {{ strengths_analyzer }} {{ challenges_critic }}",
  "variables": {
    "topic": "renewable energy"
  }
}
```

#### List Ensembles

```bash
# List all ensemble configurations
ingen ensemble list

# Show detailed information
ingen ensemble list --verbose

# Filter by strategy
ingen ensemble list --strategy parallel
```

#### Execute Ensembles

```bash
# Execute with variables
ingen ensemble run my-analysis --variables '{"topic": "AI ethics"}'

# Execute from file
ingen ensemble run my-analysis --variables-file vars.json

# Save results to file
ingen ensemble run my-analysis --output results.json

# Real-time progress display
ingen ensemble run my-analysis --progress
```

#### Ensemble Information

```bash
# Show ensemble details
ingen ensemble show my-analysis

# Show execution history
ingen ensemble history my-analysis

# Show performance metrics
ingen ensemble stats my-analysis
```

#### Update Ensembles

```bash
# Update configuration
ingen ensemble update my-analysis --config new-config.json

# Update strategy
ingen ensemble update my-analysis --strategy sequential

# Update timeout
ingen ensemble update my-analysis --timeout 600
```

#### Delete Ensembles

```bash
# Delete ensemble configuration
ingen ensemble delete my-analysis

# Force delete without confirmation
ingen ensemble delete my-analysis --force
```

## Advanced Features

### Template Management

```bash
# Create template from existing ensemble
ingen ensemble template my-analysis --output template.json

# Apply template to new ensemble
ingen ensemble create new-analysis --template template.json

# List available templates
ingen ensemble templates
```

### Batch Operations

```bash
# Execute multiple ensembles
ingen ensemble batch-run config1,config2,config3

# Run with different variable sets
ingen ensemble batch-run my-analysis --variables-dir ./variables/

# Parallel batch execution
ingen ensemble batch-run --parallel --max-concurrent 3
```

### Export and Import

```bash
# Export ensemble configuration
ingen ensemble export my-analysis --output config.json

# Import ensemble configuration
ingen ensemble import --config config.json

# Bulk export
ingen ensemble export-all --output-dir ./configs/

# Bulk import
ingen ensemble import-all --input-dir ./configs/
```

## Configuration Commands

### View Configuration

```bash
# Show current configuration
ingen config show

# Show specific section
ingen config show azure

# Show in different format
ingen config show --format yaml
```

### Update Configuration

```bash
# Set configuration value
ingen config set azure.openai.model gpt-4

# Set from file
ingen config load config.yaml

# Reset to defaults
ingen config reset

# Validate configuration
ingen config validate
```

## Diagnostic Commands

### Health Checks

```bash
# Check system health
ingen health

# Check specific services
ingen health --services azure,storage

# Detailed health report
ingen health --verbose

# Export health report
ingen health --output health-report.json
```

### Performance Monitoring

```bash
# Show performance metrics
ingen metrics

# Real-time monitoring
ingen metrics --watch

# Export metrics
ingen metrics --export metrics.json

# Historical metrics
ingen metrics --history 7d
```

## Global Options

All commands support these global options:

```bash
# Verbose output
ingen --verbose ensemble list

# Quiet mode (minimal output)
ingen --quiet ensemble run my-analysis

# Custom config file
ingen --config custom-config.yaml ensemble list

# Working directory
ingen --workdir /path/to/project dev

# Output format
ingen --format json ensemble list
```

## Environment Variables

Configure CLI behavior with environment variables:

```bash
# Default configuration file
export INGENIOUS_CONFIG_FILE="/path/to/config.yaml"

# Working directory
export INGENIOUS_WORKING_DIR="/path/to/project"

# Output format preference
export INGENIOUS_OUTPUT_FORMAT="json"

# Disable colored output
export INGENIOUS_NO_COLOR="true"

# Debug mode
export INGENIOUS_DEBUG="true"
```

## Shell Completion

Enable shell completion for enhanced CLI experience:

### Bash

```bash
# Add to ~/.bashrc
eval "$(_INGEN_COMPLETE=bash_source ingen)"
```

### Zsh

```bash
# Add to ~/.zshrc
eval "$(_INGEN_COMPLETE=zsh_source ingen)"
```

### Fish

```bash
# Add to ~/.config/fish/config.fish
eval (env _INGEN_COMPLETE=fish_source ingen)
```

## Examples

### Development Workflow

```bash
# 1. Initialize project
ingen init ai-analysis-project
cd ai-analysis-project

# 2. Create ensemble
ingen ensemble create topic-analyzer --config analyzer-config.json

# 3. Test ensemble
ingen ensemble run topic-analyzer --variables '{"topic": "climate change"}'

# 4. Start development server
ingen dev

# 5. Monitor performance
ingen metrics --watch
```

### Production Deployment

```bash
# 1. Validate configuration
ingen config validate

# 2. Run health checks
ingen health --services all

# 3. Start production server
ingen run --host 0.0.0.0 --port 8000 --workers 4

# 4. Monitor in separate terminal
ingen metrics --watch
```

### Batch Analysis

```bash
# 1. Prepare variable files
mkdir variables
echo '{"topic": "renewable energy"}' > variables/energy.json
echo '{"topic": "artificial intelligence"}' > variables/ai.json

# 2. Run batch analysis
ingen ensemble batch-run topic-analyzer --variables-dir variables/

# 3. Collect results
ingen ensemble export-results --output-dir results/
```

## Troubleshooting

### Common CLI Issues

**Command Not Found**
```bash
# Verify installation
python -c "import ingenious; print('OK')"

# Use full module path
python -m ingenious.cli --help
```

**Configuration Errors**
```bash
# Validate configuration
ingen config validate

# Reset to defaults
ingen config reset

# Check configuration file location
ingen config show --debug
```

**Permission Errors**
```bash
# Check working directory permissions
ls -la $INGENIOUS_WORKING_DIR

# Use different working directory
ingen --workdir /tmp/ingenious-temp dev
```

For more troubleshooting help, see the [Troubleshooting Guide](troubleshooting.md).
