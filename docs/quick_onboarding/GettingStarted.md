# Basic Onboarding

> This is a very simple guide just to get you started playing with the Ingenious playground.

Overall steps:
1. Clone the repo or get it via pip (and download dependencies of course, unless you don't wanna test)
2. Initialize the project
3. Run the test project.


## Clone the repo / Install via pip

```bash
# Clone the repository
git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
cd Insight_Ingenious

# Install dependencies (make sure you have installed uv before doing this)
uv venv
uv pip install -e .

# Initialize project
ingen_cli initialize-new-project
```
## Initializing the project
Once you ran `ingen_cli` successfully, you need to deal with two configuration files--`config.yml` and `profiles.yml`.

### Configuration Files
1. Edit `config.yml` in your project directory (**_Note: you may need to coordinate with your team lead with this so that you may be provided the necessary credentials._**)
2. Create or edit `profiles.yml` in `~/.ingenious/`
3. Set environment variables. Replace `path/to/your/project` below with an actual file path, then run this in your terminal application:
   ```bash
   export INGENIOUS_PROJECT_PATH=/path/to/your/project/config.yml
   export INGENIOUS_PROFILE_PATH=~/.ingenious/profiles.yml
   ```

## Testing out the CLI

### Initialize a new project

```bash
ingen_cli initialize-new-project
```

This creates the necessary folder structure and configuration files.

### Start the Application

```bash
ingen_cli run-project
```

Starts the FastAPI server with Chainlit UI.

### Testing the UI

Once the application is running, access the web UI at:
- http://localhost:8000 - Main application
- http://localhost:8000/chainlit - Chainlit chat interface
- http://localhost:8000/prompt-tuner - Prompt tuning interface

### Testing chat with the agents

1. Navigate to http://localhost:8000/chainlit
2. Start a new conversation
3. Type your message
4. The appropriate agents will process your request and respond

> **Once you are able to run those commands successfully, being able to access the UI, and has loaded the sample prompts, you're good to go! (start reading more advanced docs.) Else, kindly let us know which step you had an issue. Other in-depth information will be discussed in other docs.**