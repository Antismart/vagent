#!/usr/bin/env python3
"""
AI Agent Marketplace with vLEI - Main FastAPI Application
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid

from models import Agent, AgentMessage, TrustPolicy, CredentialVerification
from services.identity_service import IdentityService
from services.trust_service import TrustService
from services.websocket_manager import ConnectionManager

# Try to import enhanced LangChain service, fallback to simple AI service
try:
    from services.langchain_enhanced import EnhancedAIService
    ai_service = EnhancedAIService()
    logger.info("Using Enhanced LangChain AI Service")
except ImportError as e:
    logger.warning(f"LangChain not available ({e}), using simple AI service")
    from services.ai_service import AIService
    ai_service = AIService()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Agent Marketplace with vLEI",
    description="A secure marketplace where AI agents interact using verifiable credentials",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
identity_service = IdentityService()
trust_service = TrustService()
manager = ConnectionManager()

# In-memory storage (replace with database in production)
agents_db: Dict[str, Agent] = {}
messages_db: List[AgentMessage] = []
trust_logs_db: List[Dict] = []

@app.get("/")
async def root():
    return {"message": "AI Agent Marketplace with vLEI is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Agent Management Endpoints
@app.post("/api/agents", response_model=Agent)
async def create_agent(agent_data: dict):
    """Create a new AI agent with vLEI binding"""
    try:
        agent_id = str(uuid.uuid4())
        
        # Initialize agent with identity
        agent = Agent(
            id=agent_id,
            name=agent_data["name"],
            organization=agent_data["organization"],
            description=agent_data.get("description", ""),
            vlei_credential=agent_data.get("vlei_credential"),
            trust_policies=agent_data.get("trust_policies", []),
            status="inactive"
        )
        
        # Verify vLEI credential if provided
        if agent.vlei_credential:
            verification = await identity_service.verify_vlei_credential(agent.vlei_credential)
            agent.credential_verified = verification.is_valid
            agent.verification_details = verification.details
        
        agents_db[agent_id] = agent
        logger.info(f"Created agent {agent.name} with ID {agent_id}")
        
        return agent
        
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/agents", response_model=List[Agent])
async def list_agents():
    """Get all registered agents"""
    return list(agents_db.values())

@app.get("/api/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get specific agent by ID"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]

@app.post("/api/agents/{agent_id}/activate")
async def activate_agent(agent_id: str):
    """Activate an agent for communication"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_db[agent_id]
    if not agent.credential_verified:
        raise HTTPException(status_code=400, detail="Agent must have verified vLEI credential")
    
    agent.status = "active"
    agent.last_active = datetime.utcnow()
    
    return {"message": f"Agent {agent.name} activated successfully"}

# Trust and Policy Endpoints
@app.post("/api/trust/verify")
async def verify_trust(source_agent_id: str, target_agent_id: str):
    """Verify trust between two agents based on policies"""
    try:
        if source_agent_id not in agents_db or target_agent_id not in agents_db:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        source_agent = agents_db[source_agent_id]
        target_agent = agents_db[target_agent_id]
        
        # Perform trust verification
        trust_result = await trust_service.verify_trust(source_agent, target_agent)
        
        # Log the trust decision
        trust_log = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "source_agent_id": source_agent_id,
            "target_agent_id": target_agent_id,
            "trust_result": trust_result,
            "policies_applied": source_agent.trust_policies
        }
        trust_logs_db.append(trust_log)
        
        return trust_result
        
    except Exception as e:
        logger.error(f"Error verifying trust: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/trust/logs")
async def get_trust_logs():
    """Get all trust verification logs"""
    return trust_logs_db

# Messaging Endpoints
@app.post("/api/messages")
async def send_message(message_data: dict):
    """Send a message between agents"""
    try:
        # Verify trust before allowing communication
        trust_result = await trust_service.verify_trust(
            agents_db[message_data["from_agent_id"]],
            agents_db[message_data["to_agent_id"]]
        )
        
        if not trust_result["allowed"]:
            raise HTTPException(
                status_code=403, 
                detail=f"Communication blocked: {trust_result['reason']}"
            )
        
        # Create message
        message = AgentMessage(
            id=str(uuid.uuid4()),
            from_agent_id=message_data["from_agent_id"],
            to_agent_id=message_data["to_agent_id"],
            content=message_data["content"],
            message_type=message_data.get("message_type", "text"),
            timestamp=datetime.utcnow()
        )
        
        messages_db.append(message)
        
        # Process with AI if needed
        if message_data.get("ai_process", False):
            ai_response = await ai_service.process_message(message, agents_db)
            if ai_response:
                messages_db.append(ai_response)
        
        # Broadcast via WebSocket
        await manager.broadcast_message(message.dict())
        
        return {"message": "Message sent successfully", "id": message.id}
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/messages")
async def get_messages(agent_id: Optional[str] = None):
    """Get messages for specific agent or all messages"""
    if agent_id:
        return [msg for msg in messages_db if msg.from_agent_id == agent_id or msg.to_agent_id == agent_id]
    return messages_db

# WebSocket endpoint for real-time communication
@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    await manager.connect(websocket, agent_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process the message (similar to send_message endpoint)
            # This allows real-time agent communication
            await manager.send_personal_message(json.dumps(message_data), agent_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, agent_id)

# Credential Verification Endpoints
@app.post("/api/credentials/verify")
async def verify_credential(credential_data: dict):
    """Verify a vLEI credential using GLEIF APIs"""
    try:
        verification = await identity_service.verify_vlei_credential(credential_data)
        return verification.dict()
    except Exception as e:
        logger.error(f"Error verifying credential: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/schemas/{schema_id}")
async def get_credential_schema(schema_id: str):
    """Get credential schema from GLEIF Schema Server"""
    try:
        schema = await identity_service.get_credential_schema(schema_id)
        return schema
    except Exception as e:
        logger.error(f"Error getting schema: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
