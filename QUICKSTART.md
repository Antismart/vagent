# 🎯 AI Agent Marketplace with vLEI - Quick Start Guide

## ✅ Project Completed Successfully!

Your full-stack AI Agent Marketplace with vLEI trust verification is ready to use.

## 🚀 Quick Start (Choose One Method)

### Method 1: Automated Setup & Start
```bash
# Run the setup script (installs everything)
./setup.sh

# Start both frontend and backend together
npm run start:dev
```

### Method 2: Manual Setup
```bash
# Install frontend dependencies
npm install

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Start the application
npm run start:dev
```

### Method 3: Start Components Separately
```bash
# Terminal 1: Start Backend
cd backend
python3 start.py

# Terminal 2: Start Frontend
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎮 Demo & Testing

Once the backend is running, populate with sample data:
```bash
npm run demo
```

This creates 4 sample agents with different trust profiles for testing.

## 🔍 What You Get

### ✨ Core Features Implemented
- ✅ **Agent Management**: Create, verify, and activate AI agents
- ✅ **vLEI Integration**: Mock credential verification (GLEIF testnet ready)
- ✅ **Trust Verification**: Policy-based trust evaluation
- ✅ **Real-time Communication**: WebSocket agent-to-agent messaging
- ✅ **AI Processing**: OpenAI integration (with mock fallback)
- ✅ **Trust Audit**: Complete logging and monitoring
- ✅ **Modern UI**: React + TypeScript + TailwindCSS

### 🏗️ Architecture
```
Frontend (React/TS)  ←→  Backend (FastAPI)  ←→  GLEIF APIs
                              ↓
                         AI Service (OpenAI)
```

### 📱 UI Pages
1. **Dashboard** - Overview of agents and trust metrics
2. **Create Agent** - Agent setup with vLEI credentials
3. **Agent Profile** - Detailed agent information
4. **Communication** - Real-time agent chat interface
5. **Trust Logs** - Audit trail of trust decisions

### 🛡️ Trust Flow
1. Agent A wants to communicate with Agent B
2. System verifies both have valid vLEI credentials  
3. Agent A's trust policies evaluated against Agent B
4. Communication allowed/blocked based on policy results
5. All decisions logged for audit

## 🧪 Example Test Scenarios

The demo creates these agents for testing:

1. **ESG Procurement Agent** (ESG: 88, EU)
   - High ESG standards (requires ESG > 85)
   - EU jurisdiction preference

2. **Supply Chain Optimizer** (ESG: 75, US)  
   - Moderate ESG requirements (ESG > 60)
   - Global reach policy

3. **Sustainable Finance Agent** (ESG: 95, EU)
   - Premium ESG standards (ESG > 90)
   - Regulated markets only

4. **Basic Trade Agent** (ESG: 45, OTHER)
   - Minimal restrictions (ESG > 30)
   - Open trading policy

### Test Communications:
- ✅ ESG Agent ↔ Supply Chain (passes ESG requirements)
- ❌ Finance Agent → Basic Trade (fails ESG 45 < 90)
- ✅ Basic Trade → Finance Agent (low requirements)

## 🔧 Configuration

### Environment Variables (Optional)
Create `backend/.env`:
```bash
# Enable real AI responses
OPENAI_API_KEY=your_openai_key_here

# GLEIF API endpoints (already configured for testnet)
GLEIF_REPORTING_API=https://reporting.testnet.gleif.org
# ... other GLEIF endpoints
```

### Development vs Production
- **Development**: Uses mock vLEI credentials and AI responses
- **Production**: Set OpenAI key for real AI, configure GLEIF credentials

## 📚 Key Files

```
vagent/
├── src/                     # React frontend
│   ├── components/Layout.tsx    # Main layout
│   ├── pages/Dashboard.tsx      # Main dashboard
│   ├── pages/CreateAgent.tsx    # Agent creation
│   ├── pages/AgentCommunication.tsx # Chat interface
│   └── services/api.ts          # API client
├── backend/                 # FastAPI backend
│   ├── main.py                  # Main FastAPI app
│   ├── models.py               # Data models
│   ├── start.py                # Startup script
│   ├── demo.py                 # Demo data script
│   └── services/               # Business logic
│       ├── identity_service.py  # vLEI verification
│       ├── ai_service.py       # AI processing
│       ├── trust_service.py    # Trust policies
│       └── websocket_manager.py # Real-time comms
├── setup.sh                # Automated setup
└── README.md               # Full documentation
```

## 🎯 Next Steps

1. **Explore the UI**: Create agents, test communications
2. **Monitor Trust**: Watch trust verification in real-time
3. **Customize Policies**: Modify trust rules and thresholds
4. **Add OpenAI**: Set API key for intelligent responses
5. **Deploy**: Follow README.md deployment section

## 🆘 Troubleshooting

**Backend won't start?**
- Check Python 3.8+ installed: `python3 --version`
- Install dependencies: `pip install -r backend/requirements.txt`

**Frontend errors?**
- Check Node.js 18+: `node --version`
- Clear cache: `rm -rf node_modules && npm install`

**WebSocket issues?**
- Ensure backend is running on port 8000
- Check browser console for errors

**Trust verification fails?**
- Verify agents have credentials
- Check trust policy rules
- Review trust logs for details

## 🎉 Success!

You now have a fully functional AI Agent Marketplace with:
- ✅ Verifiable credential integration
- ✅ Trust-based communication
- ✅ AI-powered agents  
- ✅ Real-time monitoring
- ✅ Complete audit trail

**Happy building! 🚀**
