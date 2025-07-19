"""
Trust Service for policy evaluation and trust verification
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from models import Agent, TrustVerificationResult, TrustPolicy

logger = logging.getLogger(__name__)

class TrustService:
    def __init__(self):
        self.default_policies = self._load_default_policies()
    
    async def verify_trust(self, source_agent: Agent, target_agent: Agent) -> Dict[str, Any]:
        """
        Verify trust between two agents based on policies and credentials
        """
        try:
            # Check if both agents have verified credentials
            if not source_agent.credential_verified or not target_agent.credential_verified:
                return {
                    "allowed": False,
                    "reason": "One or both agents lack verified vLEI credentials",
                    "score": 0.0,
                    "policies_passed": [],
                    "policies_failed": ["credential_verification"],
                    "verification_details": {
                        "source_verified": source_agent.credential_verified,
                        "target_verified": target_agent.credential_verified
                    }
                }
            
            # Apply source agent's trust policies to target agent
            policy_results = []
            policies_passed = []
            policies_failed = []
            
            # Use source agent's policies or default policies
            policies_to_check = source_agent.trust_policies if source_agent.trust_policies else self.default_policies
            
            for policy in policies_to_check:
                result = await self._evaluate_policy(policy, target_agent)
                policy_results.append(result)
                
                if result["passed"]:
                    policies_passed.append(policy.name)
                else:
                    policies_failed.append(policy.name)
            
            # Calculate overall trust score
            trust_score = self._calculate_trust_score(policy_results)
            
            # Determine if communication is allowed
            allowed = trust_score >= 0.7 and len(policies_failed) == 0
            
            reason = "Trust verification passed" if allowed else f"Failed policies: {', '.join(policies_failed)}"
            
            return {
                "allowed": allowed,
                "reason": reason,
                "score": trust_score,
                "policies_passed": policies_passed,
                "policies_failed": policies_failed,
                "verification_details": {
                    "policy_results": policy_results,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error verifying trust: {str(e)}")
            return {
                "allowed": False,
                "reason": f"Trust verification error: {str(e)}",
                "score": 0.0,
                "policies_passed": [],
                "policies_failed": ["system_error"],
                "verification_details": {"error": str(e)}
            }
    
    async def _evaluate_policy(self, policy: TrustPolicy, target_agent: Agent) -> Dict[str, Any]:
        """
        Evaluate a specific trust policy against target agent
        """
        try:
            rules = policy.rules
            policy_result = {
                "policy_name": policy.name,
                "passed": True,
                "details": {},
                "score": 1.0
            }
            
            # Extract agent metadata for policy evaluation
            agent_data = self._extract_agent_data(target_agent)
            
            # Evaluate each rule in the policy
            for rule_name, rule_config in rules.items():
                rule_result = await self._evaluate_rule(rule_name, rule_config, agent_data)
                
                policy_result["details"][rule_name] = rule_result
                
                if not rule_result["passed"]:
                    policy_result["passed"] = False
                    policy_result["score"] *= 0.5  # Reduce score for failed rules
            
            return policy_result
            
        except Exception as e:
            logger.error(f"Error evaluating policy {policy.name}: {str(e)}")
            return {
                "policy_name": policy.name,
                "passed": False,
                "details": {"error": str(e)},
                "score": 0.0
            }
    
    async def _evaluate_rule(self, rule_name: str, rule_config: Dict[str, Any], agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a specific rule against agent data
        """
        try:
            if rule_name == "esg_score":
                return self._evaluate_esg_rule(rule_config, agent_data)
            elif rule_name == "jurisdiction":
                return self._evaluate_jurisdiction_rule(rule_config, agent_data)
            elif rule_name == "organization_size":
                return self._evaluate_size_rule(rule_config, agent_data)
            elif rule_name == "sector":
                return self._evaluate_sector_rule(rule_config, agent_data)
            else:
                # Unknown rule - assume passed for flexibility
                return {"passed": True, "reason": f"Unknown rule {rule_name} - skipped"}
                
        except Exception as e:
            return {"passed": False, "reason": f"Rule evaluation error: {str(e)}"}
    
    def _evaluate_esg_rule(self, rule_config: Dict[str, Any], agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate ESG score rule"""
        esg_score = agent_data.get("esg_score", 50)  # Default moderate score
        min_score = rule_config.get("min", 0)
        max_score = rule_config.get("max", 100)
        
        passed = min_score <= esg_score <= max_score
        return {
            "passed": passed,
            "reason": f"ESG score {esg_score} {'meets' if passed else 'does not meet'} requirement ({min_score}-{max_score})",
            "value": esg_score,
            "requirement": rule_config
        }
    
    def _evaluate_jurisdiction_rule(self, rule_config: Dict[str, Any], agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate jurisdiction rule"""
        agent_jurisdiction = agent_data.get("jurisdiction", "UNKNOWN")
        
        allowed_jurisdictions = rule_config.get("allowed", [])
        blocked_jurisdictions = rule_config.get("blocked", [])
        preferred_jurisdictions = rule_config.get("preferred", [])
        
        # Check blocked first
        if blocked_jurisdictions and agent_jurisdiction in blocked_jurisdictions:
            return {
                "passed": False,
                "reason": f"Jurisdiction {agent_jurisdiction} is blocked",
                "value": agent_jurisdiction,
                "requirement": rule_config
            }
        
        # Check allowed
        if allowed_jurisdictions and agent_jurisdiction not in allowed_jurisdictions:
            return {
                "passed": False,
                "reason": f"Jurisdiction {agent_jurisdiction} is not in allowed list",
                "value": agent_jurisdiction,
                "requirement": rule_config
            }
        
        # Preferred jurisdictions get bonus points but don't fail
        is_preferred = agent_jurisdiction in preferred_jurisdictions if preferred_jurisdictions else True
        
        return {
            "passed": True,
            "reason": f"Jurisdiction {agent_jurisdiction} is {'preferred' if is_preferred else 'acceptable'}",
            "value": agent_jurisdiction,
            "requirement": rule_config,
            "preferred": is_preferred
        }
    
    def _evaluate_size_rule(self, rule_config: Dict[str, Any], agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate organization size rule"""
        size = agent_data.get("organization_size", "medium")
        allowed_sizes = rule_config.get("allowed", ["small", "medium", "large", "enterprise"])
        
        passed = size in allowed_sizes
        return {
            "passed": passed,
            "reason": f"Organization size {size} {'is' if passed else 'is not'} in allowed list",
            "value": size,
            "requirement": rule_config
        }
    
    def _evaluate_sector_rule(self, rule_config: Dict[str, Any], agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate sector rule"""
        sector = agent_data.get("sector", "unknown")
        allowed_sectors = rule_config.get("allowed", [])
        blocked_sectors = rule_config.get("blocked", [])
        
        if blocked_sectors and sector in blocked_sectors:
            return {
                "passed": False,
                "reason": f"Sector {sector} is blocked",
                "value": sector,
                "requirement": rule_config
            }
        
        if allowed_sectors and sector not in allowed_sectors:
            return {
                "passed": False,
                "reason": f"Sector {sector} is not in allowed list",
                "value": sector,
                "requirement": rule_config
            }
        
        return {
            "passed": True,
            "reason": f"Sector {sector} is acceptable",
            "value": sector,
            "requirement": rule_config
        }
    
    def _extract_agent_data(self, agent: Agent) -> Dict[str, Any]:
        """
        Extract relevant data from agent for policy evaluation
        """
        # Get data from agent metadata and verification details
        agent_data = agent.metadata.copy() if agent.metadata else {}
        
        if agent.verification_details:
            agent_data.update(agent.verification_details)
        
        # Extract from vLEI credential if available
        if agent.vlei_credential:
            credential_subject = agent.vlei_credential.get("credentialSubject", {})
            agent_data.update(credential_subject)
        
        # Add default values for common fields
        defaults = {
            "esg_score": 75,  # Default moderate ESG score
            "jurisdiction": "EU",  # Default jurisdiction
            "organization_size": "medium",
            "sector": "technology"
        }
        
        for key, default_value in defaults.items():
            if key not in agent_data:
                agent_data[key] = default_value
        
        return agent_data
    
    def _calculate_trust_score(self, policy_results: List[Dict[str, Any]]) -> float:
        """
        Calculate overall trust score from policy results
        """
        if not policy_results:
            return 0.0
        
        total_score = sum(result["score"] for result in policy_results)
        return min(total_score / len(policy_results), 1.0)
    
    def _load_default_policies(self) -> List[TrustPolicy]:
        """
        Load default trust policies
        """
        return [
            TrustPolicy(
                id="default-esg",
                name="ESG Compliance",
                description="Minimum ESG score requirement",
                rules={
                    "esg_score": {"min": 60}
                }
            ),
            TrustPolicy(
                id="default-jurisdiction",
                name="Jurisdiction Trust",
                description="Acceptable jurisdictions for business",
                rules={
                    "jurisdiction": {
                        "preferred": ["EU", "US", "CA", "UK", "AU"],
                        "blocked": ["SANCTIONED"]
                    }
                }
            )
        ]
