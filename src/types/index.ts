export interface Agent {
  id: string;
  name: string;
  organization: string;
  description: string;
  vlei_credential?: any;
  credential_verified: boolean;
  verification_details?: any;
  trust_policies: TrustPolicy[];
  status: 'active' | 'inactive' | 'suspended';
  created_at: string;
  last_active?: string;
  metadata: Record<string, any>;
}

export interface TrustPolicy {
  id: string;
  name: string;
  description: string;
  rules: Record<string, any>;
  created_at: string;
}

export interface AgentMessage {
  id: string;
  from_agent_id: string;
  to_agent_id: string;
  content: string;
  message_type: 'text' | 'credential_request' | 'credential_response' | 'policy_check' | 'ai_response';
  timestamp: string;
  trust_verified: boolean;
  ai_processed: boolean;
  metadata: Record<string, any>;
}

export interface TrustVerificationResult {
  allowed: boolean;
  reason: string;
  score: number;
  policies_passed: string[];
  policies_failed: string[];
  verification_details: Record<string, any>;
}

export interface TrustLog {
  id: string;
  timestamp: string;
  source_agent_id: string;
  target_agent_id: string;
  trust_result: TrustVerificationResult;
  policies_applied: TrustPolicy[];
}

export interface CredentialVerification {
  credential_id: string;
  is_valid: boolean;
  verification_date: string;
  issuer: string;
  subject: string;
  details: Record<string, any>;
  gleif_response?: Record<string, any>;
}
