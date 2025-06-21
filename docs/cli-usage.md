# CLI Usage Guide

The Ingenious CLI (`ingen`) provides powerful command-line tools for managing AI ensembles, running applications, and development workflows.

## Installation Verification

After installing Ingenious, verify the CLI is available:

```bash
# With uv
uv run ingen --help

# If installed globally
ingen --help
```

## Core Commands

### Project Management

#### Initialize a New Project

```bash
# Initialize in current directory
ingen init
```

This creates:
- `config.yml` - Main application configuration
- `profiles.yml` - API keys and secrets
- `.gitignore` - Git ignore rules
- `SETUP.md` - Detailed setup instructions
- Directory structure (`data/`, `files/`, `.tmp/`)

#### Development Server

```bash
# Start development server (quick mode)
ingen dev
```

This starts the server with default settings for the current project directory.

#### Production Server

```bash
# Start server with default settings
ingen run

# Specify custom configuration
ingen run --project-dir /path/to/project --profile-dir /path/to/profiles

# Custom host and port
ingen run --host 0.0.0.0 --port 8080

# Full example
ingen run --project-dir ./config --profile-dir ./secrets --host 127.0.0.1 --port 8000
```

**Available Options:**
- `--project-dir`: Directory containing `config.yml` file (default: current directory)
- `--profile-dir`: Directory containing `profiles.yml` file (default: current directory)
- `--host`: Host to bind to (default: 127.0.0.1)
- `--port`: Port to run the server on (default: 8000)

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
# Execute with input file
ingen ensemble execute config-id --input data.json

# Execute with direct text input
ingen ensemble execute config-id --text "Analyze artificial intelligence trends"

# Save results to file
ingen ensemble execute config-id --input data.json --output results.json
```

#### Ensemble Information

```bash
# Show ensemble details
ingen ensemble get config-id

# Show template details
ingen ensemble get config-id --templates

# List execution history
ingen ensemble executions --config-id config-id

# Get specific execution result
ingen ensemble result execution-id --agents
```

#### Create Predefined Ensembles

```bash
# Create a multi-perspective analysis ensemble
ingen ensemble create-predefined multi_perspective_analysis topic-analyzer

# Available predefined types: multi_perspective_analysis, document_review, code_review, research_synthesis
ingen ensemble create-predefined document_review contract-analyzer
```

#### Generate Sample Configurations

```bash
# Generate basic sample configuration
ingen ensemble sample-config config.json --ensemble-type basic

# Generate advanced sample configuration
ingen ensemble sample-config config.json --ensemble-type advanced
```



## Examples

### Development Workflow

```bash
# 1. Initialize project
ingen init
cd my-project

# 2. Create ensemble
ingen ensemble create topic-analyzer --config analyzer-config.json

# 3. Test ensemble
ingen ensemble execute config-id --input test-data.json

# 4. Start development server
ingen dev
```
