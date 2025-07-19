# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

# AI Agent Marketplace with vLEI

A secure AI agent marketplace where autonomous agents interact on behalf of organizations using vLEI (Verifiable Legal Entity Identifier) credentials for trust verification.

## 🎯 Overview

This full-stack application enables AI agents to communicate securely using verifiable organizational credentials. Agents can only interact when their organizations meet specific trust policies, creating a secure and compliant environment for business automation.

## ✨ Key Features

- **🤖 AI Agent Management**: Create and manage AI agents with organizational profiles
- **🔐 vLEI Integration**: Verify organizational credentials using GLEIF testnet APIs
- **🛡️ Trust Verification**: Policy-based trust evaluation between agents
- **💬 Real-time Communication**: WebSocket-powered agent-to-agent messaging
- **🧠 AI Processing**: OpenAI-powered intelligent agent responses
- **📊 Trust Audit**: Complete logging and monitoring of trust decisions
- **🎨 Modern UI**: Clean React interface with real-time status updates

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend     │    │  GLEIF Testnet  │
│   React + TS    │◄──►│    FastAPI      │◄──►│   vLEI APIs     │
│   TailwindCSS   │    │   WebSockets    │    │  Verification   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   OpenAI API    │
                       │  Agent Brain    │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vagent
   ```

2. **Setup Frontend**
   ```bash
   npm install
   ```

3. **Setup Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   # Copy environment template
   cp backend/.env.example backend/.env
   
   # Optional: Add your OpenAI API key for AI responses
   # OPENAI_API_KEY=your_key_here
   ```

### Running the Application

1. **Start the Backend** (Terminal 1)
   ```bash
   cd backend
   python main.py
   ```
   Backend runs on: http://localhost:8000

2. **Start the Frontend** (Terminal 2)
   ```bash
   npm run dev
   ```
   Frontend runs on: http://localhost:5173

## 🎮 Usage Guide

### 1. Create Your First Agent

1. Navigate to the dashboard
2. Click "Create Agent"
3. Fill in organization details:
   - Agent name and description
   - Organization information
   - ESG score and jurisdiction
   - Trust policies (ESG thresholds, jurisdiction preferences)

### 2. Verify Credentials

- The system automatically creates mock vLEI credentials for development
- Credentials are verified using GLEIF testnet APIs (with mock fallback)
- Verified agents can be activated for communication

### 3. Test Agent Communication

1. Go to "Communication" page
2. Select source and target agents
3. Test trust verification between agents
4. Send messages and observe AI responses
5. Monitor trust decisions in real-time

### 4. Monitor Trust Logs

- View all trust verification decisions
- Filter by allowed/blocked communications
- Audit policy enforcement
- Analyze trust scores and patterns

## 🧪 Example Scenario

**ESG Procurement Use Case:**

1. **Company A** creates an ESG Procurement Agent
   - ESG Score: 85
   - Jurisdiction: EU
   - Trust Policy: Only work with partners ESG > 80

2. **Supplier B** creates a Supply Agent
   - ESG Score: 92
   - Jurisdiction: EU
   - Verified vLEI credential

3. **Communication Flow:**
   - A's agent contacts B's agent
   - Trust verification: ✅ PASS (ESG 92 > 80, EU jurisdiction trusted)
   - AI conversation proceeds
   - Trust decision logged

4. **Blocked Communication:**
   - If Supplier C has ESG score 60
   - Trust verification: ❌ FAIL (ESG 60 < 80 threshold)
   - Communication blocked and logged

## 🔧 Technical Details

### Backend API Endpoints

- `POST /api/agents` - Create new agent
- `GET /api/agents` - List all agents
- `POST /api/agents/{id}/activate` - Activate agent
- `POST /api/trust/verify` - Verify trust between agents
- `POST /api/messages` - Send agent message
- `GET /api/trust/logs` - Get trust audit logs
- `WS /ws/{agent_id}` - WebSocket for real-time updates

### Trust Policy Engine

Trust policies are evaluated using configurable rules:

```json
{
  "esg_score": {"min": 80},
  "jurisdiction": {
    "allowed": ["EU", "US", "CA"],
    "blocked": ["SANCTIONED"]
  },
  "sector": {
    "allowed": ["technology", "finance"]
  }
}
```

### vLEI Integration

- **Credential Verification**: GLEIF Presentation Handler API
- **Schema Validation**: GLEIF Schema Server
- **Trust Network**: GLEIF Reporting API
- **Mock Mode**: Development credentials for testing

## 🌐 GLEIF Testnet Integration

The application integrates with GLEIF testnet APIs:

- **Reporting API**: `https://reporting.testnet.gleif.org`
- **Schema Server**: `https://schema.testnet.gleif.org`
- **Presentation Handler**: `https://presentation-handler.testnet.gleif.org`

## 🔍 Development

### Project Structure

```
vagent/
├── src/                    # React frontend
│   ├── components/         # UI components
│   ├── pages/             # Page components
│   ├── services/          # API client
│   └── types/             # TypeScript definitions
├── backend/               # FastAPI backend
│   ├── services/          # Business logic
│   ├── models.py          # Data models
│   └── main.py           # FastAPI app
└── README.md
```

### Adding New Trust Policies

1. Define policy rules in `trust_service.py`
2. Add UI controls in `CreateAgent.tsx`
3. Update policy evaluation logic
4. Test with different agent combinations

### Extending AI Capabilities

1. Modify `ai_service.py` prompts
2. Add new message types in `models.py`
3. Update frontend message handling
4. Test conversation flows

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check Python version (3.8+)
   - Verify all dependencies installed
   - Check port 8000 is available

2. **Frontend build errors**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check Node.js version (18+)

3. **WebSocket connection fails**
   - Ensure backend is running
   - Check browser console for errors
   - Verify agent is selected

4. **Trust verification always fails**
   - Check agent credentials are verified
   - Review trust policy rules
   - Check trust logs for details

### Development Mode Features

- Mock vLEI credentials automatically generated
- AI responses use simple rule-based logic without OpenAI API
- GLEIF API calls fall back to mock data
- All data stored in-memory (resets on restart)

## 🚀 Deployment

For production deployment:

1. **Backend**
   - Deploy FastAPI with Gunicorn/Uvicorn
   - Set up PostgreSQL database
   - Configure real GLEIF API credentials
   - Add OpenAI API key for AI features

2. **Frontend**
   - Build for production: `npm run build`
   - Deploy static files to CDN
   - Update API base URL

3. **Environment**
   - Set up HTTPS for WebSocket connections
   - Configure CORS for production domains
   - Set up monitoring and logging

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or issues:
- Open a GitHub issue
- Check the troubleshooting section
- Review the API documentation at http://localhost:8000/docs

---

**Built with ❤️ for secure AI agent communication using verifiable credentials.**

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
# vagent
