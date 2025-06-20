# Insight Ingenious Features Inventory

This document catalogs all features in the Insight Ingenious codebase that can potentially be stripped or removed to create a lighter version of the framework.

## 🏗️ Core Framework Components

### ✅ Essential (Keep These)
- **Multi-Agent Framework Base** (`ingenious/services/chat_services/multi_agent/service.py`)
- **Configuration System** (`ingenious/config/`)
- **Basic Agent Model** (`ingenious/models/agent.py`)
- **Chat Interface Models** (`ingenious/models/chat.py`)
- **Core Logging** (`ingenious/core/logging.py`)
- **Dependencies Injection** (`ingenious/dependencies.py`)
- **Basic CLI Structure** (`ingenious/cli.py`)

### 🔧 API Layer

#### Keep Options
- **FastAPI Integration** (`ingenious/main.py`)
  - REST API endpoints
  - CORS middleware
  - Exception handling

#### Removable API Routes
- [X] **Chat Endpoint** (`ingenious/api/routes/chat.py`) - Essential for API access
- [X] **Diagnostic Endpoints** (`ingenious/api/routes/diagnostic.py`) - Health checks, debugging
- [X] **Message Feedback** (`ingenious/api/routes/message_feedback.py`) - User feedback collection
- [X] **Prompts Management** (`ingenious/api/routes/prompts.py`) - Prompt tuning API
- [X] **Events API** (`ingenious/api/routes/events.py`) - Event tracking
- [X] **Conversation Management** (`ingenious/api/routes/conversation.py`) - Conversation history

## 🤖 Agent System Components

### Core Agent Types (Choose What to Keep)
- [X] **Classification Agent** (`conversation_flows/classification_agent/`) - Routes to specialized agents
- [X] **Knowledge Base Agent** (`conversation_flows/knowledge_base_agent/`) - Document retrieval and Q&A
- [ ] **Pandas Agent** (`conversation_flows/pandas_agent/`) - Data analysis and visualization
- [ ] **SQL Manipulation Agent** (`conversation_flows/sql_manipulation_agent/`) - Database queries
- [ ] **Web Critic Agent** (`conversation_flows/web_critic_agent/`) - Web search and fact-checking
- [ ] **Education Expert** (`conversation_patterns/education_expert/`) - Educational content creation

### Pre-built Agent Examples
- [ ] **Lesson Planner Agent** (`agents/lesson_planner/`) - Curriculum planning
- [ ] **Education Expert Agent** (`agents/education_expert/`) - General education assistance
- [ ] **Curriculum Expert Agent** (`agents/curriculum_expert/`) - Curriculum development
- [X] **Bicycle Expert Agent** (Template) - Example domain expert

## 💾 Storage & Database Features

### Database Support (Choose What to Keep)
- [X] **SQLite Support** (`ingenious/db/sqlite/`) - Local file database
- [ ] **Azure Cosmos DB** (`ingenious/db/cosmos/`) - Cloud NoSQL database
- [ ] **DuckDB Support** (`ingenious/db/duckdb/`) - Analytics database
- [ ] **Chat History Repository** (`ingenious/db/chat_history_repository.py`) - Conversation persistence

### File Storage Options
- [X] **Local File Storage** (`ingenious/files/local/`) - Local file system
- [ ] **Azure Blob Storage** (`ingenious/files/azure/`) - Cloud storage
- [ ] **File Versioning** - Revision control for files
- [X] **Template Management** - Prompt template storage

## 🌐 Web Interface Components

### UI Components (Optional)
- [ ] **Chainlit Integration** (`ingenious/chainlit/`) - Web chat interface
  - `app.py` - Chainlit application
  - `datalayer.py` - Data layer
  - `index.html` - Landing page
- [ ] **Prompt Tuner UI** (`ingenious_prompt_tuner/`) - Flask-based prompt development tool
  - Flask web application
  - Static assets and templates
  - Authentication system
  - Event processing

## 🔧 Tool & Service Integrations

### Cloud Services (Azure-specific)
- [X] **Azure OpenAI Service** (`ingenious/external_services/openai_service.py`) - LLM integration
- [ ] **Azure Search Integration** - Knowledge base search
- [ ] **Azure SQL Database** - Enterprise database connectivity
- [ ] **Azure Key Vault** - Secrets management
- [ ] **Azure Identity** - Authentication

### Data Processing Tools
- [ ] **Scrapfly Web Crawler** (`ingenious/dataprep/crawl/`) - Web scraping capabilities
  - Batch processing
  - Rate limiting
  - Retry mechanisms
- [ ] **PDF Processing** - Document ingestion
- [ ] **CSV/Excel Processing** - Data file handling

### Analytics & Visualization
- [ ] **Matplotlib Integration** - Chart generation
- [ ] **Seaborn Plotting** - Statistical visualizations
- [ ] **Pandas Data Analysis** - Data manipulation
- [ ] **NumPy Support** - Numerical computing

## 📊 Monitoring & Development Tools

### Development Features
- [X] **Pre-commit Hooks** - Code quality checks
- [ ] **Pytest Testing Framework** - Unit and integration tests
- [X] **Ruff Linting** - Code formatting and linting
- [ ] **Vulture Dead Code Detection** - Unused code removal

### Monitoring & Logging
- [ ] **Color Logging** (`colorlog`) - Enhanced console output
- [ ] **LLM Usage Tracking** - Token consumption monitoring
- [ ] **Event Processing** - System event handling
- [ ] **Performance Metrics** - Response time tracking

### Debugging Tools
- [ ] **Memory Management** - Context memory handling
- [X] **Token Counting** (`ingenious/utils/token_counter.py`) - LLM token usage
- [ ] **Stage Executor** (`ingenious/utils/stage_executor.py`) - Pipeline execution
- [ ] **Model Utilities** (`ingenious/utils/model_utils.py`) - Model management helpers

## 🔌 Extension System

### Extensibility Features
- [X] **Custom Agent Framework** - Plugin system for new agents
- [X] **Custom API Routes** - Extension API endpoints
- [X] **Template Engine** (Jinja2) - Dynamic prompt generation
- [ ] **Namespace Utilities** - Dynamic module loading
- [ ] **Configuration Profiles** - Environment-specific settings

### Sample Extensions
- [ ] **Docker Templates** - Containerization examples
- [ ] **Sample Data** - Testing datasets (bicycle data, etc.)
- [ ] **Example Configurations** - Template config files
- [ ] **Setup Documentation** - Comprehensive guides

## 📱 CLI Features

### Command Categories
- [X] **Project Initialization** (`initialize-new-project`) - Scaffold new projects
- [X] **Server Management** (`run-rest-api-server`, `run-project`) - Start/stop services
- [ ] **Data Preparation** (`dataprep crawl`, `dataprep batch`) - Web scraping commands
- [ ] **Testing Commands** (`run-test-batch`) - Automated testing
- [ ] **Prompt Tuner** (`run-prompt-tuner`) - Development tools

## 🔒 Security & Authentication

### Authentication Systems
- [X] **Basic HTTP Authentication** - Simple user/password
- [ ] **GitHub OAuth Integration** - Social login
- [ ] **API Key Management** - Service authentication
- [ ] **Content Filtering** - Response safety checks

## 📦 Package Dependencies

### Heavy Dependencies (Consider Removing)
- [X] **AutoGen Framework** (`autogen>=0.5.3`) - Multi-agent orchestration
- [ ] **Chainlit** (`chainlit==2.5.5`) - Web UI framework
- [ ] **ChromaDB** (`chromadb==1.0.11`) - Vector database
- [ ] **Azure SDK Suite** - Multiple Azure service clients
- [ ] **Matplotlib/Seaborn** - Visualization libraries
- [ ] **IPython** - Interactive Python shell
- [ ] **Flask** - Additional web framework

### Core Dependencies (Keep)
- **FastAPI** - Main web framework
- **Pydantic** - Data validation
- **OpenAI** - LLM client
- **Typer** - CLI framework
- **Jinja2** - Template engine

## 🎯 Feature Removal Recommendations

### Minimal Core (90% size reduction)
Keep only:
- Basic agent framework
- Configuration system
- Single conversation pattern
- Local storage only
- Essential CLI commands
- Basic API endpoints

### Standard Version (70% size reduction)
Remove:
- All cloud integrations
- Web UI components
- Data processing tools
- Monitoring systems
- Pre-built agents

### Enterprise Version (30% size reduction)
Remove only:
- Example agents
- Development tools
- Sample data
- Documentation templates

## 🔄 Dependency Analysis

### High-Impact Removals
1. **Remove Chainlit** → Eliminates web UI entirely
2. **Remove Azure SDK** → Eliminates cloud dependencies
3. **Remove AutoGen** → Simplifies agent system
4. **Remove Data Tools** → Eliminates pandas, matplotlib, etc.
5. **Remove Web Crawling** → Eliminates scrapfly dependencies

### Configuration Simplification
- Remove profile system complexity
- Simplify to single config file
- Remove cloud-specific settings
- Eliminate authentication options

---

**Instructions for Use:**
1. Review each section and mark features to remove with ❌
2. Consider dependencies between features before removal
3. Test thoroughly after each major component removal
4. Update documentation to reflect removed features
