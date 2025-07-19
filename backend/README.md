# AI Agent Marketplace Backend

## Environment Configuration

Create a `.env` file in the backend directory with the following variables:

```bash
# OpenAI API (optional - will use mock responses if not provided)
OPENAI_API_KEY=your_openai_api_key_here

# GLEIF API Configuration (for production)
GLEIF_REPORTING_API=https://reporting.testnet.gleif.org
GLEIF_SCHEMA_SERVER=https://schema.testnet.gleif.org
GLEIF_PRESENTATION_HANDLER=https://presentation-handler.testnet.gleif.org
GLEIF_WEBHOOK=https://hook.testnet.gleif.org

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO

# Database (optional - using in-memory for now)
DATABASE_URL=sqlite:///./agents.db
```

## Installation

1. Install Python 3.8+ and create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Backend

```bash
# Development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python main.py
```

The API will be available at http://localhost:8000

## API Documentation

Once running, visit:
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Key Features

- **Agent Management**: Create and manage AI agents with vLEI credentials
- **Trust Verification**: Policy-based trust evaluation between agents
- **Real-time Communication**: WebSocket support for agent-to-agent messaging
- **Credential Verification**: Integration with GLEIF testnet APIs
- **AI Processing**: OpenAI-powered agent responses (with mock fallback)
