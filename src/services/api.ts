import axios from 'axios';
import type { Agent, AgentMessage, TrustVerificationResult, TrustLog, CredentialVerification } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const agentAPI = {
  // Agent management
  async createAgent(agentData: Partial<Agent>): Promise<Agent> {
    const response = await api.post('/api/agents', agentData);
    return response.data;
  },

  async getAgents(): Promise<Agent[]> {
    const response = await api.get('/api/agents');
    return response.data;
  },

  async getAgent(agentId: string): Promise<Agent> {
    const response = await api.get(`/api/agents/${agentId}`);
    return response.data;
  },

  async activateAgent(agentId: string): Promise<{ message: string }> {
    const response = await api.post(`/api/agents/${agentId}/activate`);
    return response.data;
  },

  // Trust verification
  async verifyTrust(sourceAgentId: string, targetAgentId: string): Promise<TrustVerificationResult> {
    const response = await api.post('/api/trust/verify', null, {
      params: {
        source_agent_id: sourceAgentId,
        target_agent_id: targetAgentId,
      },
    });
    return response.data;
  },

  async getTrustLogs(): Promise<TrustLog[]> {
    const response = await api.get('/api/trust/logs');
    return response.data;
  },

  // Messaging
  async sendMessage(messageData: {
    from_agent_id: string;
    to_agent_id: string;
    content: string;
    message_type?: string;
    ai_process?: boolean;
  }): Promise<{ message: string; id: string }> {
    const response = await api.post('/api/messages', messageData);
    return response.data;
  },

  async getMessages(agentId?: string): Promise<AgentMessage[]> {
    const response = await api.get('/api/messages', {
      params: agentId ? { agent_id: agentId } : {},
    });
    return response.data;
  },

  // Credential verification
  async verifyCredential(credentialData: any): Promise<CredentialVerification> {
    const response = await api.post('/api/credentials/verify', credentialData);
    return response.data;
  },

  async getCredentialSchema(schemaId: string): Promise<any> {
    const response = await api.get(`/api/schemas/${schemaId}`);
    return response.data;
  },

  // Health check
  async getHealth(): Promise<{ status: string; timestamp: string }> {
    const response = await api.get('/health');
    return response.data;
  },
};

export class WebSocketService {
  private ws: WebSocket | null = null;
  private agentId: string | null = null;
  private listeners: ((data: any) => void)[] = [];

  connect(agentId: string) {
    this.agentId = agentId;
    const wsUrl = `ws://localhost:8000/ws/${agentId}`;
    
    this.ws = new WebSocket(wsUrl);
    
    this.ws.onopen = () => {
      console.log(`WebSocket connected for agent ${agentId}`);
    };
    
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.listeners.forEach(listener => listener(data));
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        if (this.agentId) {
          this.connect(this.agentId);
        }
      }, 3000);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.agentId = null;
    this.listeners = [];
  }

  sendMessage(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  addListener(listener: (data: any) => void) {
    this.listeners.push(listener);
  }

  removeListener(listener: (data: any) => void) {
    this.listeners = this.listeners.filter(l => l !== listener);
  }
}

export const webSocketService = new WebSocketService();
