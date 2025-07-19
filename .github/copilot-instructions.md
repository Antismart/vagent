<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AI Agent Marketplace with vLEI - Copilot Instructions

## Project Overview
This is a full-stack application that creates a secure AI agent marketplace using vLEI (Verifiable Legal Entity Identifier) for trust verification. AI agents autonomously interact on behalf of organizations, but only when those organizations are verified with vLEI credentials.

## Architecture
- **Frontend**: React + TypeScript + TailwindCSS + Vite
- **Backend**: FastAPI + Python with WebSocket support
- **Identity Layer**: KERI/Signify-ts integration with GLEIF testnet APIs
- **AI Processing**: OpenAI API integration (with mock fallback)

## Key Components

### Backend (`/backend/`)
- `main.py`: FastAPI application with WebSocket support
- `models.py`: Pydantic models for agents, messages, trust policies
- `services/`: Core business logic
  - `identity_service.py`: vLEI credential verification via GLEIF APIs
  - `ai_service.py`: OpenAI-powered agent communication
  - `trust_service.py`: Policy-based trust verification
  - `websocket_manager.py`: Real-time communication management

### Frontend (`/src/`)
- React components with TypeScript
- TailwindCSS for styling
- Real-time WebSocket communication
- Trust verification visualization

## Development Guidelines

### Code Style
- Use TypeScript for all React components
- Follow React functional component patterns with hooks
- Use Pydantic models for all API data structures
- Implement proper error handling and loading states

### Trust Verification Flow
1. Agent A wants to communicate with Agent B
2. System verifies both agents have valid vLEI credentials
3. Agent A's trust policies are applied to Agent B's credentials
4. Communication is allowed/blocked based on policy results
5. All decisions are logged for audit

### Mock vs Production
- Development mode uses mock vLEI credentials and AI responses
- Set OPENAI_API_KEY environment variable to enable real AI processing
- GLEIF testnet integration is available but falls back to mocks

### Testing Scenarios
- Create agents with different ESG scores and jurisdictions
- Test trust policies (ESG thresholds, jurisdiction preferences)
- Simulate agent-to-agent conversations
- Monitor trust verification logs

## API Patterns
- All endpoints return consistent error responses
- WebSocket connections are per-agent for real-time updates
- Trust verification is performed before any agent communication
- Credentials are verified using GLEIF Presentation Handler API

## UI/UX Guidelines
- Use status badges for agent states (active/inactive, verified/unverified)
- Show trust scores as percentages with color coding
- Provide real-time feedback for WebSocket connections
- Make trust verification results clearly visible

## Security Considerations
- All agent communication requires verified vLEI credentials
- Trust policies are enforced before message delivery
- Credential verification uses cryptographic proofs
- Communication logs provide audit trail
