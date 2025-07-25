# KloudPortal SEO CrewAI Bot

A sophisticated SEO blog commenting automation system using CrewAI and Google Vertex AI.

## 🚀 Features

- **CrewAI Multi-Agent System**: Specialized agents for blog research, content analysis, comment generation, and quality review
- **Cost-Optimized Vertex AI**: Smart model selection between Gemini Flash and Pro with budget tracking
- **Structured Logging**: Rich console output and file logging for debugging
- **CLI Interface**: Beautiful command-line interface with Rich and Typer
- **Phase-Based Development**: Modular development approach with detailed documentation

## 📋 Phase 1: Foundation Complete ✅

Phase 1 includes:
- Project structure and environment setup
- Vertex AI integration with cost optimization
- Database models (ready for Phase 4)
- CLI interface with setup, cost reporting, and testing commands
- Comprehensive testing suite (6/6 tests passing)

## 🛠️ Installation

### Prerequisites
- Python 3.10+ (< 3.13)
- Google Cloud Project with Vertex AI enabled
- Service account with appropriate permissions

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/anandvijay96/kp-crewai-bot.git
   cd kp-crewai-bot
   ```

2. **Install dependencies using uv**
   ```bash
   # Install uv if not already installed
   # Windows PowerShell: 
   irm https://astral.sh/uv/install.ps1 | iex
   
   # Create virtual environment and install dependencies
   uv venv
   # Activate virtual environment
   # Windows: .venv\Scripts\activate
   # Unix: source .venv/bin/activate
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Google Cloud project details
   ```

4. **Add Google Cloud credentials**
   - Place your service account JSON key in `credentials/vertex-ai-key.json`
   - Ensure your service account has these roles:
     - `Vertex AI User`
     - `AI Platform Developer`

## 🧪 Testing

Run the setup check:
```bash
python -m src.seo_automation.main setup
```

View cost report:
```bash
python -m src.seo_automation.main cost-report
```

Test Vertex AI connection:
```bash
python -m src.seo_automation.main test-model --model-type flash --prompt "Hello world"
```

Run all tests:
```bash
python tests/test_phase1.py
```

## 📊 Available Commands

- `setup` - Validate configuration and test connections
- `cost-report` - Display current usage and budget status  
- `test-model` - Test Vertex AI models with custom prompts
- `info` - Show system information
- `--help` - Display all available commands

## 🏗️ Project Structure

```
kp-crewai-bot/
├── src/seo_automation/          # Main application code
│   ├── config/                  # Configuration management
│   ├── utils/                   # Utilities (Vertex AI, logging, database)
│   ├── agents/                  # CrewAI agents (Phase 2)
│   ├── tasks/                   # CrewAI tasks (Phase 2)
│   ├── tools/                   # CrewAI tools (Phase 2)
│   └── main.py                  # CLI entry point
├── tests/                       # Test suite
├── data/                        # Data directories
│   ├── input/                   # Input files
│   ├── output/                  # Generated outputs
│   └── logs/                    # Application logs
├── docs/                        # Documentation
└── Docs/                        # Phase documentation
```

## 🔧 Configuration

Key environment variables in `.env`:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./credentials/vertex-ai-key.json

# Cost Management
DAILY_BUDGET_USD=15.0
COST_ALERT_THRESHOLD=0.8

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## 📈 Development Phases

- ✅ **Phase 1**: Foundation & Core Setup (Complete)
- 🚧 **Phase 2**: Agent Development (Next)
- 📋 **Phase 3**: Core Workflows
- 📋 **Phase 4**: Integration & Enhancement
- 📋 **Phase 5**: API & Interface
- 📋 **Phase 6**: Production Readiness

See detailed phase documentation in the `Docs/` folder.

## 🤝 Contributing

This is a private project for KloudPortal's SEO automation needs. 

## 📝 License

Private project - All rights reserved.

## 🆘 Troubleshooting

### Common Issues

1. **Vertex AI Permission Denied**
   - Ensure your service account has `Vertex AI User` and `AI Platform Developer` roles
   - Verify the JSON key path in `.env` is correct

2. **Module Import Errors**
   - Make sure virtual environment is activated
   - Run `uv sync` to install all dependencies

3. **Configuration Issues**
   - Run `python -m src.seo_automation.main setup` to validate configuration
   - Check that all required environment variables are set

### Getting Help

- Check logs in `data/logs/application.log`
- Run `python -m src.seo_automation.main info` for system status
- Verify configuration with the setup command

---

**Status**: Phase 1 Complete ✅ | Ready for Phase 2 Development 🚀
