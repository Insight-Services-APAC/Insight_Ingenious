---
title: "Quick Onboarding"
layout: single
permalink: /quick_onboarding/
sidebar:
  nav: "docs"
toc: true
toc_label: "Onboarding Steps"
toc_icon: "rocket"
---

# Basic Onboarding

> This is a very simple guide just to get you started playing with the Ingenious playground.

Overall steps:
1. Clone the repo or get it via pip (and download dependencies of course, unless you don't wanna test)
2. Initialize the project
3. Run the test project.


## Clone the repo / Install via pip

```bash
# Clone the repository
git clone https://github.com/Insight-Services-APAC/ingenious.git
cd ingenious

# Install dependencies (make sure you have installed uv before doing this)
uv venv
uv pip install -e .

# Initialize project
uv run ingen init
```
## Initializing the project
Once you ran `uv run ingen init` successfully, you need to deal with two configuration files--`config.yml` and `profiles.yml`.

### Configuration Files
1. Edit `config.yml` in your project directory (**_Note: you may need to coordinate with your team lead with this so that you may be provided the necessary credentials._**)
2. Create or edit `profiles.yml` in `path/to/your/project`
3. Set environment variables. Replace `path/to/your/project` below with an actual file path, then run this in your terminal application:
   #### For Linux-based Environments
   ```bash
   export INGENIOUS_PROJECT_PATH=/path/to/your/project/config.yml
   export INGENIOUS_PROFILE_PATH=/path/to/your/project/profiles.yml
   ```

   #### For Windows-based Environments
    ```powershell
    $env:INGENIOUS_PROJECT_PATH = "{your_project_folder}/config.yml"
    $env:INGENIOUS_PROFILE_PATH = "{profile_folder_location}/profiles.yml"
    ```

## Testing out the CLI

### Initialize a new project

```bash
uv run ingen init
```

This creates the necessary folder structure and configuration files.

### Check Workflow Requirements

Before starting, understand what each workflow needs:

```bash
# See all available workflows and their requirements
uv run ingen workflows

# Check specific workflow requirements
uv run ingen workflows classification-agent
```

### Start with Minimal Configuration

For quick testing, start with workflows that only need Azure OpenAI:

1. Update `config.yml` with your Azure OpenAI model settings
2. Update `profiles.yml` with your API key and endpoint
3. Set environment variables:
   ```bash
   export INGENIOUS_PROJECT_PATH=/path/to/config.yml
   export INGENIOUS_PROFILE_PATH=/path/to/profiles.yml
   ```

### Start the Application

```bash
uv run ingen serve
```

Starts the FastAPI server with Chainlit UI.

### Testing the UI

Once the application is running, access the web UI at:
- http://localhost:80 - Main application
- http://localhost:80/chainlit - Chainlit chat interface
- http://localhost:80/prompt-tuner - Prompt tuning interface

### Testing chat with the agents

#### Quick Test (Minimal Configuration)
Test with workflows that only need Azure OpenAI:

1. Navigate to http://localhost:80/chainlit
2. Start a new conversation
3. Try these workflows:
   - "Hello" with `classification-agent`
   - "Analyze bike sales" with `bike-insights`

#### API Testing
```bash
# Test classification agent (minimal config needed)
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Hello world", "conversation_flow": "classification-agent"}'
```

#### Advanced Workflows
For workflows requiring external services:

- **knowledge-base-agent**: Requires Azure Cognitive Search
- **sql-manipulation-agent**: Requires database connection

Check requirements with:
```bash
uv run ingen workflows <workflow_name>
```

See [Workflow Configuration Requirements](../workflows/README.md) for detailed setup.

> **Once you are able to run those commands successfully, access the UI, and test basic workflows, you're good to go! For advanced workflows requiring external services, check their specific configuration requirements.**

Next up: Building custom agents. Go to **CustomAgents.md**
