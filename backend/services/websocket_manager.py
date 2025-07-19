"""
WebSocket Connection Manager for real-time communication
"""

from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.agent_connections: Dict[str, str] = {}  # agent_id -> connection_id
    
    async def connect(self, websocket: WebSocket, agent_id: str):
        """Accept websocket connection and associate with agent"""
        await websocket.accept()
        connection_id = f"conn_{len(self.active_connections)}"
        self.active_connections[connection_id] = websocket
        self.agent_connections[agent_id] = connection_id
        logger.info(f"Agent {agent_id} connected via WebSocket")
    
    def disconnect(self, websocket: WebSocket, agent_id: str):
        """Remove websocket connection"""
        connection_id = self.agent_connections.get(agent_id)
        if connection_id and connection_id in self.active_connections:
            del self.active_connections[connection_id]
            del self.agent_connections[agent_id]
            logger.info(f"Agent {agent_id} disconnected from WebSocket")
    
    async def send_personal_message(self, message: str, agent_id: str):
        """Send message to specific agent"""
        connection_id = self.agent_connections.get(agent_id)
        if connection_id and connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to agent {agent_id}: {str(e)}")
                # Remove broken connection
                self.disconnect(websocket, agent_id)
    
    async def broadcast_message(self, message: dict):
        """Broadcast message to all connected agents"""
        message_text = json.dumps(message)
        disconnected_connections = []
        
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message_text)
            except Exception as e:
                logger.error(f"Error broadcasting to connection {connection_id}: {str(e)}")
                disconnected_connections.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected_connections:
            if connection_id in self.active_connections:
                # Find agent_id for this connection
                agent_id = None
                for aid, cid in self.agent_connections.items():
                    if cid == connection_id:
                        agent_id = aid
                        break
                
                if agent_id:
                    del self.agent_connections[agent_id]
                del self.active_connections[connection_id]
    
    def get_connected_agents(self) -> List[str]:
        """Get list of currently connected agent IDs"""
        return list(self.agent_connections.keys())
