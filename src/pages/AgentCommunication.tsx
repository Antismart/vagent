import React, { useState, useEffect } from 'react';
import { 
  ChatBubbleLeftRightIcon, 
  PaperAirplaneIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import type { Agent, AgentMessage } from '../types';
import { agentAPI, webSocketService } from '../services/api';

export const AgentCommunication: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [selectedFromAgent, setSelectedFromAgent] = useState<string>('');
  const [selectedToAgent, setSelectedToAgent] = useState<string>('');
  const [messageContent, setMessageContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    loadData();
    
    // WebSocket listener for real-time messages
    const handleMessage = (data: any) => {
      if (data.type === 'message') {
        setMessages(prev => [...prev, data.message]);
      }
    };
    
    webSocketService.addListener(handleMessage);
    
    return () => {
      webSocketService.removeListener(handleMessage);
    };
  }, []);

  useEffect(() => {
    // Connect WebSocket when agent is selected
    if (selectedFromAgent) {
      webSocketService.connect(selectedFromAgent);
      setWsConnected(true);
    }
    
    return () => {
      if (wsConnected) {
        webSocketService.disconnect();
        setWsConnected(false);
      }
    };
  }, [selectedFromAgent]);

  const loadData = async () => {
    try {
      const [agentsData, messagesData] = await Promise.all([
        agentAPI.getAgents(),
        agentAPI.getMessages()
      ]);
      setAgents(agentsData);
      setMessages(messagesData);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFromAgent || !selectedToAgent || !messageContent.trim()) {
      return;
    }

    setLoading(true);
    try {
      await agentAPI.sendMessage({
        from_agent_id: selectedFromAgent,
        to_agent_id: selectedToAgent,
        content: messageContent,
        ai_process: true
      });
      
      setMessageContent('');
      await loadData(); // Refresh messages
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message. Check trust policies and verification status.');
    } finally {
      setLoading(false);
    }
  };

  const testTrustVerification = async () => {
    if (!selectedFromAgent || !selectedToAgent) {
      alert('Please select both source and target agents');
      return;
    }

    try {
      const trustResult = await agentAPI.verifyTrust(selectedFromAgent, selectedToAgent);
      
      const resultMessage = `Trust Verification Result:
- Allowed: ${trustResult.allowed}
- Score: ${(trustResult.score * 100).toFixed(0)}%
- Reason: ${trustResult.reason}
- Policies Passed: ${trustResult.policies_passed.join(', ') || 'None'}
- Policies Failed: ${trustResult.policies_failed.join(', ') || 'None'}`;
      
      alert(resultMessage);
    } catch (error) {
      console.error('Error testing trust:', error);
      alert('Failed to test trust verification');
    }
  };

  const activeAgents = agents.filter(agent => agent.status === 'active');
  const verifiedAgents = agents.filter(agent => agent.credential_verified);

  const getMessageStyle = (message: AgentMessage) => {
    const isFromSelected = message.from_agent_id === selectedFromAgent;
    return isFromSelected
      ? 'ml-auto bg-blue-500 text-white'
      : 'mr-auto bg-gray-200 text-gray-900';
  };

  const getAgentName = (agentId: string) => {
    const agent = agents.find(a => a.id === agentId);
    return agent ? agent.name : 'Unknown Agent';
  };

  const conversationMessages = messages.filter(
    msg => 
      (msg.from_agent_id === selectedFromAgent && msg.to_agent_id === selectedToAgent) ||
      (msg.from_agent_id === selectedToAgent && msg.to_agent_id === selectedFromAgent)
  ).sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Agent Communication</h1>
        <p className="mt-2 text-gray-600">
          Test agent-to-agent communication with trust verification
        </p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <ShieldCheckIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Agents</p>
              <p className="text-2xl font-bold text-gray-900">{agents.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active</p>
              <p className="text-2xl font-bold text-gray-900">{activeAgents.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <ShieldCheckIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Verified</p>
              <p className="text-2xl font-bold text-gray-900">{verifiedAgents.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <ChatBubbleLeftRightIcon className="h-6 w-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Messages</p>
              <p className="text-2xl font-bold text-gray-900">{messages.length}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Agent Selection & Controls */}
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Select Agents</h2>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="fromAgent" className="block text-sm font-medium text-gray-700 mb-2">
                  From Agent (Source)
                </label>
                <select
                  id="fromAgent"
                  value={selectedFromAgent}
                  onChange={(e) => setSelectedFromAgent(e.target.value)}
                  className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select source agent...</option>
                  {agents.map(agent => (
                    <option key={agent.id} value={agent.id}>
                      {agent.name} ({agent.organization}) - {agent.status}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="toAgent" className="block text-sm font-medium text-gray-700 mb-2">
                  To Agent (Target)
                </label>
                <select
                  id="toAgent"
                  value={selectedToAgent}
                  onChange={(e) => setSelectedToAgent(e.target.value)}
                  className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select target agent...</option>
                  {agents.map(agent => (
                    <option key={agent.id} value={agent.id} disabled={agent.id === selectedFromAgent}>
                      {agent.name} ({agent.organization}) - {agent.status}
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={testTrustVerification}
                disabled={!selectedFromAgent || !selectedToAgent}
                className="w-full btn-secondary disabled:opacity-50"
              >
                <ShieldCheckIcon className="w-4 h-4 mr-2" />
                Test Trust Verification
              </button>
            </div>
          </div>

          {/* WebSocket Status */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Connection Status</h3>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-gray-400'}`}></div>
              <span className="text-sm text-gray-600">
                {wsConnected ? 'WebSocket Connected' : 'WebSocket Disconnected'}
              </span>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Messages</h3>
            <div className="space-y-2">
              {[
                "Hello! I'm interested in exploring partnership opportunities.",
                "Could you share your ESG credentials for review?",
                "Our organization is looking for sustainable suppliers.",
                "What are your capabilities in the technology sector?"
              ].map((quickMsg, index) => (
                <button
                  key={index}
                  onClick={() => setMessageContent(quickMsg)}
                  className="w-full text-left p-2 text-sm bg-gray-50 hover:bg-gray-100 rounded border"
                  disabled={!selectedFromAgent || !selectedToAgent}
                >
                  {quickMsg}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="lg:col-span-2">
          <div className="card h-full flex flex-col">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Conversation</h2>
              {selectedFromAgent && selectedToAgent && (
                <div className="text-sm text-gray-600">
                  {getAgentName(selectedFromAgent)} ↔ {getAgentName(selectedToAgent)}
                </div>
              )}
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto border border-gray-200 rounded-lg p-4 mb-4 h-96">
              {!selectedFromAgent || !selectedToAgent ? (
                <div className="flex items-center justify-center h-full text-gray-500">
                  Select both agents to start a conversation
                </div>
              ) : conversationMessages.length === 0 ? (
                <div className="flex items-center justify-center h-full text-gray-500">
                  No messages yet. Send the first message!
                </div>
              ) : (
                <div className="space-y-4">
                  {conversationMessages.map((message) => (
                    <div key={message.id} className="flex">
                      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${getMessageStyle(message)}`}>
                        <div className="text-xs mb-1 opacity-75">
                          {getAgentName(message.from_agent_id)}
                          {message.message_type === 'ai_response' && ' (AI)'}
                        </div>
                        <div className="text-sm">{message.content}</div>
                        <div className="text-xs mt-1 opacity-75">
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Message Input */}
            <form onSubmit={sendMessage} className="flex space-x-2">
              <input
                type="text"
                value={messageContent}
                onChange={(e) => setMessageContent(e.target.value)}
                placeholder="Type your message..."
                disabled={!selectedFromAgent || !selectedToAgent || loading}
                className="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={!selectedFromAgent || !selectedToAgent || !messageContent.trim() || loading}
                className="btn-primary disabled:opacity-50"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <PaperAirplaneIcon className="w-4 h-4" />
                )}
              </button>
            </form>

            {/* Trust Warning */}
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-start">
                <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400 mt-0.5" />
                <div className="ml-3">
                  <p className="text-sm text-yellow-800">
                    <strong>Trust Verification:</strong> Messages will only be delivered if trust policies pass. 
                    Failed trust checks will be logged and communication blocked.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
