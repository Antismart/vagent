        Use this format when using tools:

        Thought: Think about what you need to do
        Action: [tool_name] 
        Action Input: [input to tool]
        Observation: [result from tool]
        ... (repeat as needed)
        Final Answer: Your response to the human

        Current conversation:
        {chat_history}

        Human: {input}
        Thought:"""
        
        return base_prompt
    
    def _get_memory(self, agent_id: str) -> ConversationBufferMemory:
        """Get or create conversation memory for agent"""
        if agent_id not in self.memories:
            self.memories[agent_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        return self.memories[agent_id]
    
    async def process_message_with_langchain(
        self, 
        message: AgentMessage, 
        from_agent: Agent, 
        to_agent: Agent,
        agents_db: Dict[str, Agent]
    ) -> Optional[str]:
        """Process message using LangChain agent"""
        try:
            # Get tools for the responding agent
            tools = self._get_agent_tools(to_agent, agents_db)
            
            # Create agent prompt
            prompt_template = self._get_agent_prompt(to_agent)
            
            # Get conversation memory
            memory = self._get_memory(to_agent.id)
            
            # Create the agent
            if tools:
                # Use ReAct agent with tools
                from langchain.agents import create_react_agent
                
                prompt = PromptTemplate.from_template(prompt_template)
                agent = create_react_agent(self.llm, tools, prompt)
                agent_executor = AgentExecutor(
                    agent=agent,
                    tools=tools,
                    memory=memory,
                    verbose=True,
                    max_iterations=3
                )
                
                # Process message
                context = f"Message from {from_agent.name} ({from_agent.organization}): {message.content}"
                response = await agent_executor.ainvoke({"input": context})
                
                return response.get("output", "I apologize, I couldn't process that request.")
            
            else:
                # Simple LLM chain without tools
                prompt = PromptTemplate(
                    template=prompt_template + "\n\nHuman: {input}\nAssistant:",
                    input_variables=["input"]
                )
                
                chain = LLMChain(llm=self.llm, prompt=prompt, memory=memory)
                
                context = f"Message from {from_agent.name} ({from_agent.organization}): {message.content}"
                response = await chain.arun(input=context)
                
                return response.strip()
                
        except Exception as e:
            logger.error(f"Error in LangChain processing: {str(e)}")
            return None
    
    async def process_message(
        self, 
        message: AgentMessage, 
        agents_db: Dict[str, Agent]
    ) -> Optional[AgentMessage]:
        """Main message processing method"""
        try:
            from_agent = agents_db.get(message.from_agent_id)
            to_agent = agents_db.get(message.to_agent_id)
            
            if not from_agent or not to_agent:
                return None
            
            # Try LangChain first, fall back to simple responses
            if self.use_langchain:
                ai_response = await self.process_message_with_langchain(
                    message, from_agent, to_agent, agents_db
                )
            else:
                ai_response = await self._generate_simple_response(
                    message, from_agent, to_agent
                )
            
            if ai_response:
                response_message = AgentMessage(
                    id=f"langchain-{datetime.utcnow().timestamp()}",
                    from_agent_id=message.to_agent_id,
                    to_agent_id=message.from_agent_id,
                    content=ai_response,
                    message_type=MessageType.AI_RESPONSE,
                    timestamp=datetime.utcnow(),
                    ai_processed=True
                )
                
                return response_message
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return None
    
    async def _generate_simple_response(
        self, 
        message: AgentMessage, 
        from_agent: Agent, 
        to_agent: Agent
    ) -> str:
        """Fallback simple response generation"""
        content_lower = message.content.lower()
        
        # Enhanced rule-based responses
        if "hello" in content_lower or "hi" in content_lower:
            return f"Hello {from_agent.name}! I'm {to_agent.name} from {to_agent.organization}. As a verified entity with vLEI credentials, I'm interested in exploring how our organizations can collaborate. What specific partnership opportunities are you considering?"
        
        elif "partnership" in content_lower or "collaborate" in content_lower:
            esg_score = to_agent.metadata.get('esg_score', 'unknown')
            return f"Thank you for your interest in partnership. {to_agent.organization} (ESG Score: {esg_score}) is always open to collaborating with verified partners. We prioritize ESG compliance and sustainable business practices. What type of partnership did you have in mind?"
        
        elif "esg" in content_lower or "sustainability" in content_lower:
            esg_score = to_agent.metadata.get('esg_score', 75)
            return f"ESG and sustainability are core to our operations. {to_agent.organization} maintains an ESG score of {esg_score} and we're committed to continuous improvement. We're particularly interested in partners who share our values. What are your organization's ESG priorities?"
        
        elif "credential" in content_lower or "verification" in content_lower:
            lei = to_agent.vlei_credential.get("credentialSubject", {}).get("lei", "Not available") if to_agent.vlei_credential else "Not available"
            return f"Our organization is verified through vLEI credentials (LEI: {lei}). This ensures trust and transparency in all our business relationships. We can provide detailed credential information if needed for partnership evaluation."
        
        elif "trust" in content_lower or "policy" in content_lower:
            policies = len(to_agent.trust_policies)
            return f"{to_agent.organization} has {policies} trust policies in place to ensure secure and compliant partnerships. Our policies cover ESG requirements, jurisdictional preferences, and sector-specific criteria. Would you like to discuss how our trust frameworks align?"
        
        else:
            sector = to_agent.metadata.get('sector', 'business')
            return f"Thank you for reaching out, {from_agent.name}. {to_agent.organization} specializes in {sector} and values trust-based partnerships. As a vLEI-verified entity, we're committed to transparent and sustainable business practices. How can we assist you today?"

# Enhanced AI Service that uses LangChain when available
class EnhancedAIService:
    """Wrapper service that uses LangChain or falls back to simple AI"""
    
    def __init__(self, trust_service=None):
        self.langchain_service = LangChainAgentService(trust_service)
        
        # Also keep the original simple service as fallback
        from ai_service import AIService
        self.simple_service = AIService()
    
    async def process_message(self, message: AgentMessage, agents_db: Dict[str, Agent]) -> Optional[AgentMessage]:
        """Process message with LangChain if available, otherwise use simple service"""
        
        # Try LangChain first
        if self.langchain_service.use_langchain:
            logger.info("Processing message with LangChain")
            result = await self.langchain_service.process_message(message, agents_db)
            if result:
                return result
        
        # Fallback to simple service
        logger.info("Processing message with simple AI service")
        return await self.simple_service.process_message(message, agents_db)
    
    async def generate_agent_profile_suggestions(self, organization: str, description: str) -> Dict[str, Any]:
        """Generate profile suggestions"""
        return await self.simple_service.generate_agent_profile_suggestions(organization, description)
