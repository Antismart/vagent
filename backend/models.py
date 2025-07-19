"""
Data models for the AI Agent Marketplace
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AgentStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    SUSPENDED = "suspended"

class MessageType(str, Enum):
    TEXT = "text"
    CREDENTIAL_REQUEST = "credential_request"
    CREDENTIAL_RESPONSE = "credential_response"
    POLICY_CHECK = "policy_check"
    AI_RESPONSE = "ai_response"

class TrustPolicy(BaseModel):
    id: str
    name: str
    description: str
    rules: Dict[str, Any]  # e.g., {"esg_score": {"min": 80}, "jurisdiction": {"allowed": ["EU", "US"]}}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CredentialVerification(BaseModel):
    credential_id: str
    is_valid: bool
    verification_date: datetime
    issuer: str
    subject: str
    details: Dict[str, Any]
    gleif_response: Optional[Dict[str, Any]] = None

class Agent(BaseModel):
    id: str
    name: str
    organization: str
    description: str = ""
    vlei_credential: Optional[Dict[str, Any]] = None
    credential_verified: bool = False
    verification_details: Optional[Dict[str, Any]] = None
    trust_policies: List[TrustPolicy] = []
    status: AgentStatus = AgentStatus.INACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

class AgentMessage(BaseModel):
    id: str
    from_agent_id: str
    to_agent_id: str
    content: str
    message_type: MessageType = MessageType.TEXT
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    trust_verified: bool = False
    ai_processed: bool = False
    metadata: Dict[str, Any] = {}

class TrustVerificationResult(BaseModel):
    allowed: bool
    reason: str
    score: float
    policies_passed: List[str]
    policies_failed: List[str]
    verification_details: Dict[str, Any]

class CredentialPresentationRequest(BaseModel):
    requester_id: str
    credential_types: List[str]
    purpose: str
    challenge: str

class CredentialPresentationResponse(BaseModel):
    responder_id: str
    credentials: List[Dict[str, Any]]
    proof: Dict[str, Any]
    challenge: str
