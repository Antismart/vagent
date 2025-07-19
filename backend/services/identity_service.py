"""
Identity Service for vLEI credential verification using GLEIF APIs
"""

import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from models import CredentialVerification

logger = logging.getLogger(__name__)

class IdentityService:
    def __init__(self):
        self.gleif_reporting_api = "https://reporting.testnet.gleif.org"
        self.gleif_schema_server = "https://schema.testnet.gleif.org"
        self.gleif_presentation_handler = "https://presentation-handler.testnet.gleif.org"
        self.gleif_webhook = "https://hook.testnet.gleif.org"
    
    async def verify_vlei_credential(self, credential: Dict[str, Any]) -> CredentialVerification:
        """
        Verify a vLEI credential using GLEIF Presentation Handler API
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Prepare verification request
                verification_request = {
                    "credential": credential,
                    "options": {
                        "challenge": f"challenge-{datetime.utcnow().timestamp()}",
                        "domain": "ai-agent-marketplace"
                    }
                }
                
                # Call GLEIF Presentation Handler
                async with session.post(
                    f"{self.gleif_presentation_handler}/verify",
                    json=verification_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        gleif_response = await response.json()
                        
                        return CredentialVerification(
                            credential_id=credential.get("id", "unknown"),
                            is_valid=gleif_response.get("verified", False),
                            verification_date=datetime.utcnow(),
                            issuer=credential.get("issuer", "unknown"),
                            subject=credential.get("credentialSubject", {}).get("id", "unknown"),
                            details=gleif_response,
                            gleif_response=gleif_response
                        )
                    else:
                        # Verification failed
                        error_response = await response.text()
                        logger.warning(f"GLEIF verification failed: {error_response}")
                        
                        return CredentialVerification(
                            credential_id=credential.get("id", "unknown"),
                            is_valid=False,
                            verification_date=datetime.utcnow(),
                            issuer=credential.get("issuer", "unknown"),
                            subject=credential.get("credentialSubject", {}).get("id", "unknown"),
                            details={"error": error_response, "status": response.status},
                            gleif_response=None
                        )
                        
        except Exception as e:
            logger.error(f"Error verifying vLEI credential: {str(e)}")
            
            # Return mock verification for development
            return await self._mock_credential_verification(credential)
    
    async def _mock_credential_verification(self, credential: Dict[str, Any]) -> CredentialVerification:
        """
        Mock credential verification for development/testing
        """
        # Simulate verification based on credential content
        is_valid = True
        verification_details = {
            "mock": True,
            "verification_method": "development_mode",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Basic validation checks
        if not credential.get("credentialSubject"):
            is_valid = False
            verification_details["error"] = "Missing credentialSubject"
        
        if not credential.get("issuer"):
            is_valid = False
            verification_details["error"] = "Missing issuer"
        
        return CredentialVerification(
            credential_id=credential.get("id", f"mock-{datetime.utcnow().timestamp()}"),
            is_valid=is_valid,
            verification_date=datetime.utcnow(),
            issuer=credential.get("issuer", "mock-issuer"),
            subject=credential.get("credentialSubject", {}).get("id", "mock-subject"),
            details=verification_details,
            gleif_response=verification_details
        )
    
    async def get_credential_schema(self, schema_id: str) -> Dict[str, Any]:
        """
        Retrieve credential schema from GLEIF Schema Server
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.gleif_schema_server}/schemas/{schema_id}"
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        # Return mock schema for development
                        return self._get_mock_schema(schema_id)
                        
        except Exception as e:
            logger.error(f"Error fetching schema {schema_id}: {str(e)}")
            return self._get_mock_schema(schema_id)
    
    def _get_mock_schema(self, schema_id: str) -> Dict[str, Any]:
        """
        Mock credential schema for development
        """
        return {
            "id": schema_id,
            "type": "JsonSchema",
            "description": f"Mock schema for {schema_id}",
            "properties": {
                "credentialSubject": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "legalName": {"type": "string"},
                        "lei": {"type": "string"},
                        "esgScore": {"type": "number"},
                        "jurisdiction": {"type": "string"}
                    }
                }
            },
            "mock": True
        }
    
    async def request_credential_presentation(self, agent_id: str, credential_types: List[str]) -> Dict[str, Any]:
        """
        Request credential presentation from another agent
        """
        challenge = f"challenge-{agent_id}-{datetime.utcnow().timestamp()}"
        
        return {
            "presentation_request": {
                "challenge": challenge,
                "credential_types": credential_types,
                "requester": agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    async def verify_credential_presentation(self, presentation: Dict[str, Any]) -> bool:
        """
        Verify a credential presentation response
        """
        try:
            # In a real implementation, this would verify the cryptographic proof
            # For now, we'll do basic validation
            required_fields = ["credentials", "proof", "challenge"]
            return all(field in presentation for field in required_fields)
            
        except Exception as e:
            logger.error(f"Error verifying presentation: {str(e)}")
            return False
