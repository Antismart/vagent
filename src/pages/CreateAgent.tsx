import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShieldCheckIcon, 
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { agentAPI } from '../services/api';
import type { TrustPolicy } from '../types';

export const CreateAgent: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    organization: '',
    description: '',
    sector: 'technology',
    jurisdiction: 'EU',
    esg_score: 75,
    organization_size: 'medium'
  });

  const [trustPolicies, setTrustPolicies] = useState<Omit<TrustPolicy, 'id' | 'created_at'>[]>([
    {
      name: 'ESG Compliance',
      description: 'Minimum ESG score requirement for partner organizations',
      rules: { esg_score: { min: 60 } }
    },
    {
      name: 'Jurisdiction Trust',
      description: 'Acceptable jurisdictions for business partnerships',
      rules: { 
        jurisdiction: { 
          preferred: ['EU', 'US', 'CA', 'UK'], 
          blocked: ['SANCTIONED'] 
        } 
      }
    }
  ]);

  const [mockCredential] = useState({
    "@context": ["https://www.w3.org/2018/credentials/v1"],
    "type": ["VerifiableCredential", "vLEICredential"],
    "issuer": "did:keri:gleif",
    "issuanceDate": new Date().toISOString(),
    "credentialSubject": {
      "id": "did:keri:example",
      "legalName": "",
      "lei": `LEI${Math.random().toString(36).substr(2, 16).toUpperCase()}`,
      "esgScore": 75,
      "jurisdiction": "EU",
      "sector": "technology"
    },
    "proof": {
      "type": "Ed25519Signature2020",
      "created": new Date().toISOString(),
      "verificationMethod": "did:keri:gleif#key-1",
      "proofPurpose": "assertionMethod",
      "proofValue": "mock-signature-for-development"
    }
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'esg_score' ? parseInt(value) : value
    }));
  };

  const handlePolicyChange = (index: number, field: string, value: any) => {
    setTrustPolicies(prev => {
      const updated = [...prev];
      if (field === 'esg_min') {
        updated[index].rules.esg_score = { min: parseInt(value) };
      } else if (field === 'name' || field === 'description') {
        updated[index][field] = value;
      }
      return updated;
    });
  };

  const addPolicy = () => {
    setTrustPolicies(prev => [...prev, {
      name: 'New Policy',
      description: 'Custom trust policy',
      rules: {}
    }]);
  };

  const removePolicy = (index: number) => {
    setTrustPolicies(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Create mock vLEI credential with form data
      const credential = {
        ...mockCredential,
        credentialSubject: {
          ...mockCredential.credentialSubject,
          legalName: formData.organization,
          esgScore: formData.esg_score,
          jurisdiction: formData.jurisdiction,
          sector: formData.sector
        }
      };

      // Convert trust policies to proper format
      const formattedPolicies: TrustPolicy[] = trustPolicies.map((policy, index) => ({
        id: `policy-${Date.now()}-${index}`,
        name: policy.name,
        description: policy.description,
        rules: policy.rules,
        created_at: new Date().toISOString()
      }));

      const agentData = {
        name: formData.name,
        organization: formData.organization,
        description: formData.description,
        vlei_credential: credential,
        trust_policies: formattedPolicies,
        metadata: {
          sector: formData.sector,
          jurisdiction: formData.jurisdiction,
          esg_score: formData.esg_score,
          organization_size: formData.organization_size
        }
      };

      const newAgent = await agentAPI.createAgent(agentData);
      navigate(`/agents/${newAgent.id}`);
    } catch (error) {
      console.error('Error creating agent:', error);
      alert('Failed to create agent. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Create AI Agent</h1>
        <p className="mt-2 text-gray-600">
          Set up a new AI agent with vLEI credentials and trust policies
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic Information */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Basic Information</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Agent Name
              </label>
              <input
                type="text"
                name="name"
                id="name"
                required
                value={formData.name}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., ESG Procurement Agent"
              />
            </div>

            <div>
              <label htmlFor="organization" className="block text-sm font-medium text-gray-700">
                Organization
              </label>
              <input
                type="text"
                name="organization"
                id="organization"
                required
                value={formData.organization}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Acme Corporation"
              />
            </div>
          </div>

          <div className="mt-6">
            <label htmlFor="description" className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              name="description"
              id="description"
              rows={3}
              value={formData.description}
              onChange={handleInputChange}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="Describe the agent's role and capabilities..."
            />
          </div>
        </div>

        {/* Organization Details */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Organization Details</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="sector" className="block text-sm font-medium text-gray-700">
                Sector
              </label>
              <select
                name="sector"
                id="sector"
                value={formData.sector}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="technology">Technology</option>
                <option value="finance">Finance</option>
                <option value="healthcare">Healthcare</option>
                <option value="manufacturing">Manufacturing</option>
                <option value="energy">Energy</option>
                <option value="retail">Retail</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label htmlFor="jurisdiction" className="block text-sm font-medium text-gray-700">
                Jurisdiction
              </label>
              <select
                name="jurisdiction"
                id="jurisdiction"
                value={formData.jurisdiction}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="EU">European Union</option>
                <option value="US">United States</option>
                <option value="CA">Canada</option>
                <option value="UK">United Kingdom</option>
                <option value="AU">Australia</option>
                <option value="OTHER">Other</option>
              </select>
            </div>

            <div>
              <label htmlFor="esg_score" className="block text-sm font-medium text-gray-700">
                ESG Score
              </label>
              <input
                type="range"
                name="esg_score"
                id="esg_score"
                min="0"
                max="100"
                value={formData.esg_score}
                onChange={handleInputChange}
                className="mt-1 block w-full"
              />
              <div className="text-sm text-gray-500 mt-1">
                Current: {formData.esg_score}/100
              </div>
            </div>

            <div>
              <label htmlFor="organization_size" className="block text-sm font-medium text-gray-700">
                Organization Size
              </label>
              <select
                name="organization_size"
                id="organization_size"
                value={formData.organization_size}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="small">Small (1-50 employees)</option>
                <option value="medium">Medium (51-500 employees)</option>
                <option value="large">Large (501-5000 employees)</option>
                <option value="enterprise">Enterprise (5000+ employees)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Trust Policies */}
        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Trust Policies</h2>
            <button
              type="button"
              onClick={addPolicy}
              className="btn-secondary"
            >
              Add Policy
            </button>
          </div>

          <div className="space-y-4">
            {trustPolicies.map((policy, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1 space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Policy Name
                      </label>
                      <input
                        type="text"
                        value={policy.name}
                        onChange={(e) => handlePolicyChange(index, 'name', e.target.value)}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Description
                      </label>
                      <input
                        type="text"
                        value={policy.description}
                        onChange={(e) => handlePolicyChange(index, 'description', e.target.value)}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    {policy.name === 'ESG Compliance' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Minimum ESG Score
                        </label>
                        <input
                          type="number"
                          min="0"
                          max="100"
                          value={policy.rules.esg_score?.min || 60}
                          onChange={(e) => handlePolicyChange(index, 'esg_min', e.target.value)}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    )}
                  </div>
                  
                  {trustPolicies.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removePolicy(index)}
                      className="ml-4 text-red-600 hover:text-red-800"
                    >
                      Remove
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* vLEI Credential Preview */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">vLEI Credential</h2>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div className="flex items-start">
              <InformationCircleIcon className="h-5 w-5 text-blue-500 mt-0.5" />
              <div className="ml-3">
                <p className="text-sm text-blue-800">
                  <strong>Development Mode:</strong> A mock vLEI credential will be created for testing. 
                  In production, this would integrate with GLEIF's credential issuance process.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-2">Generated Credential Preview</h3>
            <div className="text-xs text-gray-600 space-y-1">
              <div><strong>Legal Name:</strong> {formData.organization || 'Your Organization'}</div>
              <div><strong>LEI:</strong> {mockCredential.credentialSubject.lei}</div>
              <div><strong>ESG Score:</strong> {formData.esg_score}</div>
              <div><strong>Jurisdiction:</strong> {formData.jurisdiction}</div>
              <div><strong>Sector:</strong> {formData.sector}</div>
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Creating Agent...
              </>
            ) : (
              <>
                <ShieldCheckIcon className="w-5 h-5 mr-2" />
                Create Agent
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
