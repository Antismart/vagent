#!/usr/bin/env python3
"""
Demo script to create sample agents and test trust verification
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def create_sample_agents():
    """Create sample agents for testing"""
    
    # Sample agent configurations
    agents = [
        {
            "name": "ESG Procurement Agent",
            "organization": "Green Tech Solutions Inc.",
            "description": "AI agent focused on sustainable procurement and ESG-compliant supplier relationships",
            "metadata": {
                "sector": "technology",
                "jurisdiction": "EU",
                "esg_score": 88,
                "organization_size": "medium"
            },
            "trust_policies": [
                {
                    "name": "ESG Excellence Standard",
                    "description": "Only partner with organizations having ESG score > 85",
                    "rules": {"esg_score": {"min": 85}}
                },
                {
                    "name": "EU Jurisdiction Preference",
                    "description": "Prefer EU-based organizations for compliance",
                    "rules": {"jurisdiction": {"preferred": ["EU", "UK"], "blocked": ["SANCTIONED"]}}
                }
            ]
        },
        {
            "name": "Supply Chain Optimizer",
            "organization": "Global Manufacturing Corp",
            "description": "Optimizes supply chain relationships with focus on efficiency and sustainability",
            "metadata": {
                "sector": "manufacturing",
                "jurisdiction": "US",
                "esg_score": 75,
                "organization_size": "large"
            },
            "trust_policies": [
                {
                    "name": "Minimum ESG Compliance",
                    "description": "Basic ESG requirements for suppliers",
                    "rules": {"esg_score": {"min": 60}}
                },
                {
                    "name": "Global Reach",
                    "description": "Accept partners from major regulated markets",
                    "rules": {"jurisdiction": {"allowed": ["US", "EU", "CA", "UK", "AU"]}}
                }
            ]
        },
        {
            "name": "Sustainable Finance Agent",
            "organization": "EcoBank International",
            "description": "Specialized in green finance and sustainable investment opportunities",
            "metadata": {
                "sector": "finance",
                "jurisdiction": "EU",
                "esg_score": 95,
                "organization_size": "enterprise"
            },
            "trust_policies": [
                {
                    "name": "Premium ESG Standards",
                    "description": "Highest ESG standards for financial partnerships",
                    "rules": {"esg_score": {"min": 90}}
                },
                {
                    "name": "Regulated Markets Only",
                    "description": "Only work with highly regulated jurisdictions",
                    "rules": {"jurisdiction": {"allowed": ["EU", "US", "UK", "CA"]}}
                }
            ]
        },
        {
            "name": "Basic Trade Agent",
            "organization": "Standard Trading Co",
            "description": "General purpose trading agent with minimal requirements",
            "metadata": {
                "sector": "retail",
                "jurisdiction": "OTHER",
                "esg_score": 45,
                "organization_size": "small"
            },
            "trust_policies": [
                {
                    "name": "Open Trading Policy",
                    "description": "Minimal restrictions for broad market access",
                    "rules": {"esg_score": {"min": 30}}
                }
            ]
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        created_agents = []
        
        for agent_config in agents:
            # Create mock vLEI credential
            vlei_credential = {
                "@context": ["https://www.w3.org/2018/credentials/v1"],
                "type": ["VerifiableCredential", "vLEICredential"],
                "issuer": "did:keri:gleif",
                "issuanceDate": datetime.utcnow().isoformat(),
                "credentialSubject": {
                    "id": f"did:keri:{agent_config['organization'].lower().replace(' ', '-')}",
                    "legalName": agent_config["organization"],
                    "lei": f"LEI{hash(agent_config['organization']) % 10000000000000000:016d}",
                    "esgScore": agent_config["metadata"]["esg_score"],
                    "jurisdiction": agent_config["metadata"]["jurisdiction"],
                    "sector": agent_config["metadata"]["sector"]
                },
                "proof": {
                    "type": "Ed25519Signature2020",
                    "created": datetime.utcnow().isoformat(),
                    "verificationMethod": "did:keri:gleif#key-1",
                    "proofPurpose": "assertionMethod",
                    "proofValue": f"mock-signature-{hash(agent_config['organization'])}"
                }
            }
            
            # Format trust policies
            formatted_policies = []
            for i, policy in enumerate(agent_config["trust_policies"]):
                formatted_policies.append({
                    "id": f"policy-{hash(agent_config['name'])}-{i}",
                    "name": policy["name"],
                    "description": policy["description"],
                    "rules": policy["rules"],
                    "created_at": datetime.utcnow().isoformat()
                })
            
            agent_data = {
                "name": agent_config["name"],
                "organization": agent_config["organization"],
                "description": agent_config["description"],
                "vlei_credential": vlei_credential,
                "trust_policies": formatted_policies,
                "metadata": agent_config["metadata"]
            }
            
            try:
                async with session.post(f"{BASE_URL}/api/agents", json=agent_data) as response:
                    if response.status == 200:
                        agent = await response.json()
                        created_agents.append(agent)
                        print(f"✅ Created agent: {agent['name']} ({agent['organization']})")
                        
                        # Activate agent if verified
                        if agent.get('credential_verified', False):
                            async with session.post(f"{BASE_URL}/api/agents/{agent['id']}/activate") as activate_response:
                                if activate_response.status == 200:
                                    print(f"🚀 Activated agent: {agent['name']}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to create agent {agent_config['name']}: {error_text}")
                        
            except Exception as e:
                print(f"❌ Error creating agent {agent_config['name']}: {str(e)}")
        
        return created_agents

async def test_agent_interactions(agents):
    """Test some agent interactions"""
    if len(agents) < 2:
        print("❌ Need at least 2 agents for interaction testing")
        return
    
    print("\n🔍 Testing agent interactions...")
    
    async with aiohttp.ClientSession() as session:
        # Test various agent combinations
        test_pairs = [
            (0, 1),  # ESG agent -> Supply Chain (should pass)
            (1, 0),  # Supply Chain -> ESG agent (should pass)
            (2, 3),  # Finance -> Basic Trade (should fail - ESG too low)
            (3, 2),  # Basic Trade -> Finance (should pass - no strict requirements)
        ]
        
        for source_idx, target_idx in test_pairs:
            if source_idx < len(agents) and target_idx < len(agents):
                source_agent = agents[source_idx]
                target_agent = agents[target_idx]
                
                print(f"\n🔄 Testing: {source_agent['name']} → {target_agent['name']}")
                
                try:
                    # Test trust verification
                    params = {
                        "source_agent_id": source_agent["id"],
                        "target_agent_id": target_agent["id"]
                    }
                    
                    async with session.post(f"{BASE_URL}/api/trust/verify", params=params) as response:
                        if response.status == 200:
                            trust_result = await response.json()
                            
                            status = "✅ ALLOWED" if trust_result["allowed"] else "❌ BLOCKED"
                            score = int(trust_result["score"] * 100)
                            
                            print(f"   {status} (Score: {score}%)")
                            print(f"   Reason: {trust_result['reason']}")
                            
                            if trust_result["allowed"]:
                                # Send a test message
                                message_data = {
                                    "from_agent_id": source_agent["id"],
                                    "to_agent_id": target_agent["id"],
                                    "content": f"Hello {target_agent['name']}! I'm {source_agent['name']} from {source_agent['organization']}. I'm interested in exploring potential partnership opportunities between our organizations.",
                                    "ai_process": True
                                }
                                
                                async with session.post(f"{BASE_URL}/api/messages", json=message_data) as msg_response:
                                    if msg_response.status == 200:
                                        print("   📨 Test message sent successfully")
                                    else:
                                        print("   ❌ Failed to send test message")
                        else:
                            error_text = await response.text()
                            print(f"   ❌ Trust verification failed: {error_text}")
                            
                except Exception as e:
                    print(f"   ❌ Error testing interaction: {str(e)}")

async def main():
    """Main demo function"""
    print("🚀 AI Agent Marketplace Demo")
    print("=" * 50)
    
    # Check if backend is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status != 200:
                    print("❌ Backend is not running. Please start it first:")
                    print("   cd backend && python main.py")
                    return
    except:
        print("❌ Cannot connect to backend. Please start it first:")
        print("   cd backend && python main.py")
        return
    
    print("✅ Backend is running")
    print("\n📝 Creating sample agents...")
    
    # Create sample agents
    agents = await create_sample_agents()
    
    if agents:
        print(f"\n✅ Created {len(agents)} agents successfully")
        
        # Test interactions
        await test_agent_interactions(agents)
        
        print("\n🎯 Demo completed!")
        print(f"🌐 Open http://localhost:5173 to explore the marketplace")
        print(f"📚 API docs: http://localhost:8000/docs")
        
        print("\n💡 Try these interactions in the UI:")
        print("   1. View agent profiles and verification status")
        print("   2. Test trust verification between agents")
        print("   3. Send messages and see AI responses")
        print("   4. Monitor trust logs and decisions")
    else:
        print("❌ Failed to create sample agents")

if __name__ == "__main__":
    asyncio.run(main())
