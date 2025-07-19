"""
AI Service for agent communication and reasoning
"""

import openai
import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from models import Agent, AgentMessage, MessageType

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        self.use_mock = not self.openai_api_key
        
    async def process_message(self, message: AgentMessage, agents_db: Dict[str, Agent]) -> Optional[AgentMessage]:
        """
        Process incoming message and generate AI response if needed
        """
        try:
            from_agent = agents_db.get(message.from_agent_id)
            to_agent = agents_db.get(message.to_agent_id)
            
            if not from_agent or not to_agent:
                return None
            
            # Generate AI response based on agent type and context
            ai_response = await self._generate_agent_response(
                message, from_agent, to_agent
            )
            
            if ai_response:
                response_message = AgentMessage(
                    id=f"ai-{datetime.utcnow().timestamp()}",
                    from_agent_id=message.to_agent_id,
                    to_agent_id=message.from_agent_id,
                    content=ai_response,
                    message_type=MessageType.AI_RESPONSE,
                    timestamp=datetime.utcnow(),
                    ai_processed=True
                )
                
                return response_message
                
        except Exception as e:
            logger.error(f"Error processing message with AI: {str(e)}")
            return None
    
    async def _generate_agent_response(self, message: AgentMessage, from_agent: Agent, to_agent: Agent) -> Optional[str]:
        """
        Generate AI response based on agent personas and message content
        """
        if self.use_mock:
            return await self._generate_mock_response(message, from_agent, to_agent)
        
        try:
            # Create agent persona and context
            system_prompt = self._build_agent_system_prompt(to_agent)
            conversation_context = self._build_conversation_context(message, from_agent, to_agent)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": conversation_context}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            return await self._generate_mock_response(message, from_agent, to_agent)
    
    def _build_agent_system_prompt(self, agent: Agent) -> str:
        """
        Build system prompt based on agent characteristics
        """
        base_prompt = f"""You are an AI agent representing {agent.organization}. 
Your name is {agent.name} and your role is: {agent.description}

Key characteristics:
- You are a professional business agent operating in a secure, verified environment
- All communications are backed by vLEI (Verifiable Legal Entity Identifier) credentials
- You should be helpful, professional, and focused on business objectives
- You can discuss partnerships, collaborations, ESG initiatives, and business opportunities
- Always maintain your organization's interests while being collaborative

Organization: {agent.organization}
Verification Status: {"Verified with vLEI" if agent.credential_verified else "Pending verification"}
"""
        
        # Add trust policy context
        if agent.trust_policies:
            policy_info = "Your organization has the following trust policies:\n"
            for policy in agent.trust_policies:
                policy_info += f"- {policy.name}: {policy.description}\n"
            base_prompt += f"\n{policy_info}"
        
        return base_prompt
    
    def _build_conversation_context(self, message: AgentMessage, from_agent: Agent, to_agent: Agent) -> str:
        """
        Build conversation context for AI processing
        """
        context = f"""
INCOMING MESSAGE:
From: {from_agent.name} ({from_agent.organization})
Message: {message.content}

CONTEXT:
- This is a secure agent-to-agent communication
- Both parties have verified credentials
- Respond professionally and focus on potential business collaboration
- If the message is asking about capabilities, describe your organization's strengths
- If discussing partnerships, consider mutual benefits and trust factors

Please respond as {to_agent.name} from {to_agent.organization}.
"""
        return context
    
    async def _generate_mock_response(self, message: AgentMessage, from_agent: Agent, to_agent: Agent) -> str:
        """
        Generate mock AI response for development/testing
        """
        # Simple rule-based responses for demo
        content_lower = message.content.lower()
        
        if "hello" in content_lower or "hi" in content_lower:
            return f"Hello {from_agent.name}! I'm {to_agent.name} from {to_agent.organization}. How can we collaborate today?"
        
        elif "partnership" in content_lower or "collaborate" in content_lower:
            return f"Thank you for reaching out about partnership opportunities. {to_agent.organization} is always interested in working with verified partners. What specific areas of collaboration are you considering?"
        
        elif "esg" in content_lower or "sustainability" in content_lower:
            return f"ESG and sustainability are core priorities for {to_agent.organization}. We'd be happy to discuss how our organizations can work together on sustainable initiatives. What are your current ESG goals?"
        
        elif "credential" in content_lower or "verification" in content_lower:
            verification_status = "verified" if to_agent.credential_verified else "in progress"
            return f"Our vLEI credential verification is {verification_status}. We maintain high standards for trust and transparency. What verification information do you need?"
        
        else:
            return f"Thank you for your message, {from_agent.name}. {to_agent.organization} appreciates your interest. Could you provide more specific details about what you'd like to discuss?"
    
    async def generate_agent_profile_suggestions(self, organization: str, description: str) -> Dict[str, Any]:
        """
        Generate AI-powered suggestions for agent configuration
        """
        if self.use_mock:
            return self._generate_mock_profile_suggestions(organization, description)
        
        try:
            prompt = f"""
Given an organization "{organization}" with description "{description}", 
suggest appropriate:
1. Trust policies (ESG requirements, jurisdiction preferences, etc.)
2. Agent personality traits
3. Preferred communication topics
4. Partnership criteria

Return as JSON format.
"""
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.5
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error generating profile suggestions: {str(e)}")
            return self._generate_mock_profile_suggestions(organization, description)
    
    def _generate_mock_profile_suggestions(self, organization: str, description: str) -> Dict[str, Any]:
        """
        Generate mock profile suggestions
        """
        return {
            "trust_policies": [
                {
                    "name": "ESG Compliance",
                    "description": "Partner organizations must have ESG score > 70",
                    "rules": {"esg_score": {"min": 70}}
                },
                {
                    "name": "Jurisdiction Trust",
                    "description": "Prefer partners from regulated jurisdictions",
                    "rules": {"jurisdiction": {"preferred": ["EU", "US", "CA", "UK"]}}
                }
            ],
            "personality_traits": [
                "Professional",
                "Collaborative",
                "Trustworthy",
                "Innovation-focused"
            ],
            "communication_topics": [
                "Partnership opportunities",
                "ESG initiatives",
                "Technology collaboration",
                "Supply chain optimization"
            ],
            "partnership_criteria": [
                "Verified legal entity status",
                "Strong ESG credentials",
                "Complementary business focus",
                "Regulatory compliance"
            ]
        }
