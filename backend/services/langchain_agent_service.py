"""
Enhanced AI Service using LangChain for sophisticated agent behaviors
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from langchain.llms import OpenAI
    from langchain.chat_models import ChatOpenAI
    from langchain.agents import create_react_agent, AgentExecutor
    from langchain.tools import BaseTool, Tool
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import BaseMessage, HumanMessage, AIMessage
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from models import Agent, AgentMessage, MessageType

logger = logging.getLogger(__name__)

class TrustVerificationTool(BaseTool):
    """Custom LangChain tool for trust verification"""
    
    name = "trust_verification"
    description = "Verify trust between two agents based on vLEI credentials and policies"
    
    def __init__(self, trust_service, agents_db):
        super().__init__()
        self.trust_service = trust_service
        self.agents_db = agents_db
    
    def _run(self, source_agent_id: str, target_agent_id: str) -> str:
        """Execute trust verification"""
        try:
            if source_agent_id not in self.agents_db or target_agent_id not in self.agents_db:
                return "Error: One or both agents not found"
            
            source_agent = self.agents_db[source_agent_id]
            target_agent = self.agents_db[target_agent_id]
            
            # This would be async in real implementation
            # For LangChain tool, we need sync version
            trust_result = {
                "allowed": True,  # Simplified for demo
                "score": 0.85,
                "reason": "Mock trust verification passed"
            }
            
            return json.dumps(trust_result)
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _arun(self, source_agent_id: str, target_agent_id: str) -> str:
        """Async version"""
        return self._run(source_agent_id, target_agent_id)

class CredentialQueryTool(BaseTool):
    """Tool for querying credential information"""
    
    name = "credential_query"
    description = "Query vLEI credential information for an agent"
    
    def __init__(self, agents_db):
        super().__init__()
        self.agents_db = agents_db
    
    def _run(self, agent_id: str) -> str:
        """Get credential info"""
        try:
            if agent_id not in self.agents_db:
                return "Error: Agent not found"
            
            agent = self.agents_db[agent_id]
            
            if not agent.vlei_credential:
                return "No vLEI credential found for this agent"
            
            credential_info = {
                "verified": agent.credential_verified,
                "organization": agent.vlei_credential.get("credentialSubject", {}).get("legalName"),
                "lei": agent.vlei_credential.get("credentialSubject", {}).get("lei"),
                "esg_score": agent.vlei_credential.get("credentialSubject", {}).get("esgScore"),
                "jurisdiction": agent.vlei_credential.get("credentialSubject", {}).get("jurisdiction"),
                "sector": agent.vlei_credential.get("credentialSubject", {}).get("sector")
            }
            
            return json.dumps(credential_info, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

class LangChainAgentService:
    """Enhanced AI service using LangChain for sophisticated agent behaviors"""
    
    def __init__(self, trust_service=None):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.trust_service = trust_service
        self.use_langchain = LANGCHAIN_AVAILABLE and self.openai_api_key
        
        if self.use_langchain:
            self.llm = ChatOpenAI(
                temperature=0.7,
                model_name="gpt-4",
                openai_api_key=self.openai_api_key
            )
            self.memories = {}  # Per-agent conversation memory
        
        logger.info(f"LangChain Agent Service initialized (LangChain: {self.use_langchain})")
    
    def _get_agent_tools(self, agent: Agent, agents_db: Dict[str, Agent]) -> List[BaseTool]:
        """Get available tools for an agent"""
        tools = []
        
        if self.trust_service:
            tools.append(TrustVerificationTool(self.trust_service, agents_db))
        
        tools.append(CredentialQueryTool(agents_db))
        
        # Add more custom tools based on agent type
        if "procurement" in agent.name.lower():
            tools.append(self._create_procurement_tool())
        elif "finance" in agent.name.lower():
            tools.append(self._create_finance_tool())
        
        return tools
    
    def _create_procurement_tool(self) -> BaseTool:
        """Create procurement-specific tool"""
        return Tool(
            name="procurement_analysis",
            description="Analyze supplier credentials for procurement decisions",
            func=lambda supplier_info: f"Procurement analysis: {supplier_info} - Evaluating ESG compliance and supply chain reliability."
        )
    
    def _create_finance_tool(self) -> BaseTool:
        """Create finance-specific tool"""
        return Tool(
            name="risk_assessment",
            description="Assess financial and ESG risks",
            func=lambda partner_info: f"Risk assessment: {partner_info} - Analyzing creditworthiness and ESG risk factors."
        )
    
    def _get_agent_prompt(self, agent: Agent) -> str:
        """Get specialized prompt for agent type"""
        base_prompt = f"""You are {agent.name}, an AI agent representing {agent.organization}.

Your role: {agent.description}

Key characteristics:
- You operate in a secure environment with vLEI-verified credentials
- You can use tools to verify trust and credentials
- You should be professional, helpful, and focused on business objectives
- Always consider ESG factors and compliance in your responses

Organization details:
- Name: {agent.organization}
- Verified: {"Yes" if agent.credential_verified else "No"}
- Sector: {agent.metadata.get('sector', 'Unknown')}
- Jurisdiction: {agent.metadata.get('jurisdiction', 'Unknown')}
- ESG Score: {agent.metadata.get('esg_score', 'Unknown')}

Available tools: {'{tools}'}
Tool names: {'{tool_names}'}

When responding:
1. Use tools when you need to verify credentials or trust
2. Be specific about your organization's capabilities and requirements
3. Consider trust policies and ESG factors in partnerships
4. Ask clarifying questions when needed
