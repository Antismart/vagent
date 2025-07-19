import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ShieldCheckIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  ArrowLeftIcon,
  PlayIcon
} from '@heroicons/react/24/outline';
import type { Agent } from '../types';
import { agentAPI } from '../services/api';

export const AgentProfile: React.FC = () => {
  const { agentId } = useParams<{ agentId: string }>();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (agentId) {
      loadAgent();
    }
  }, [agentId]);

  const loadAgent = async () => {
    try {
      setLoading(true);
      const agentData = await agentAPI.getAgent(agentId!);
      setAgent(agentData);
    } catch (err) {
      setError('Failed to load agent data');
      console.error('Agent loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const activateAgent = async () => {
    if (!agent) return;
    
    try {
      await agentAPI.activateAgent(agent.id);
      await loadAgent(); // Refresh data
    } catch (err) {
      console.error('Error activating agent:', err);
      alert('Failed to activate agent. Check if vLEI credential is verified.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !agent) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <XCircleIcon className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="mt-1 text-sm text-red-700">{error || 'Agent not found'}</p>
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    const colors = {
      active: 'text-green-600 bg-green-100',
      inactive: 'text-gray-600 bg-gray-100',
      suspended: 'text-red-600 bg-red-100'
    };
    return colors[status as keyof typeof colors] || colors.inactive;
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link to="/" className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-4">
          <ArrowLeftIcon className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Link>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{agent.name}</h1>
            <p className="mt-2 text-gray-600">{agent.organization}</p>
            <p className="mt-1 text-gray-500">{agent.description}</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className={`status-badge ${getStatusColor(agent.status)}`}>
              {agent.status}
            </span>
            
            {agent.status === 'inactive' && agent.credential_verified && (
              <button
                onClick={activateAgent}
                className="btn-primary"
              >
                <PlayIcon className="w-4 h-4 mr-2" />
                Activate Agent
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center">
            <div className={`p-2 rounded-lg ${agent.credential_verified ? 'bg-green-100' : 'bg-yellow-100'}`}>
              {agent.credential_verified ? (
                <CheckCircleIcon className="h-6 w-6 text-green-600" />
              ) : (
                <XCircleIcon className="h-6 w-6 text-yellow-600" />
              )}
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">vLEI Verification</p>
              <p className="text-lg font-bold text-gray-900">
                {agent.credential_verified ? 'Verified' : 'Pending'}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <ShieldCheckIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Trust Policies</p>
              <p className="text-lg font-bold text-gray-900">{agent.trust_policies.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <ShieldCheckIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Last Active</p>
              <p className="text-lg font-bold text-gray-900">
                {agent.last_active ? new Date(agent.last_active).toLocaleDateString() : 'Never'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Agent Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Organization Details */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Organization Details</h2>
          
          <dl className="space-y-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Organization</dt>
              <dd className="text-sm text-gray-900">{agent.organization}</dd>
            </div>
            
            <div>
              <dt className="text-sm font-medium text-gray-500">Sector</dt>
              <dd className="text-sm text-gray-900">{agent.metadata.sector || 'Not specified'}</dd>
            </div>
            
            <div>
              <dt className="text-sm font-medium text-gray-500">Jurisdiction</dt>
              <dd className="text-sm text-gray-900">{agent.metadata.jurisdiction || 'Not specified'}</dd>
            </div>
            
            <div>
              <dt className="text-sm font-medium text-gray-500">ESG Score</dt>
              <dd className="text-sm text-gray-900">{agent.metadata.esg_score || 'Not specified'}</dd>
            </div>
            
            <div>
              <dt className="text-sm font-medium text-gray-500">Organization Size</dt>
              <dd className="text-sm text-gray-900 capitalize">{agent.metadata.organization_size || 'Not specified'}</dd>
            </div>
            
            <div>
              <dt className="text-sm font-medium text-gray-500">Created</dt>
              <dd className="text-sm text-gray-900">{new Date(agent.created_at).toLocaleString()}</dd>
            </div>
          </dl>
        </div>

        {/* Trust Policies */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Trust Policies</h2>
          
          {agent.trust_policies.length === 0 ? (
            <p className="text-gray-500">No trust policies configured</p>
          ) : (
            <div className="space-y-4">
              {agent.trust_policies.map((policy) => (
                <div key={policy.id} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900">{policy.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{policy.description}</p>
                  
                  <div className="mt-3">
                    <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider">Rules</h4>
                    <div className="mt-2 text-xs text-gray-700">
                      <pre className="whitespace-pre-wrap">{JSON.stringify(policy.rules, null, 2)}</pre>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* vLEI Credential */}
      {agent.vlei_credential && (
        <div className="card mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">vLEI Credential</h2>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Legal Name</dt>
                <dd className="text-sm text-gray-900">{agent.vlei_credential.credentialSubject?.legalName}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">LEI</dt>
                <dd className="text-sm text-gray-900 font-mono">{agent.vlei_credential.credentialSubject?.lei}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Issuer</dt>
                <dd className="text-sm text-gray-900">{agent.vlei_credential.issuer}</dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Issuance Date</dt>
                <dd className="text-sm text-gray-900">
                  {new Date(agent.vlei_credential.issuanceDate).toLocaleDateString()}
                </dd>
              </div>
            </div>
            
            <details className="mt-4">
              <summary className="text-sm font-medium text-gray-700 cursor-pointer">
                View Full Credential
              </summary>
              <pre className="mt-2 text-xs text-gray-600 whitespace-pre-wrap overflow-x-auto">
                {JSON.stringify(agent.vlei_credential, null, 2)}
              </pre>
            </details>
          </div>
        </div>
      )}

      {/* Verification Details */}
      {agent.verification_details && (
        <div className="card mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Verification Details</h2>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <pre className="text-xs text-gray-600 whitespace-pre-wrap">
              {JSON.stringify(agent.verification_details, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};
