import React, { useState, useEffect } from 'react';
import { 
  ShieldCheckIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  ClockIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';
import type { TrustLog, Agent } from '../types';
import { agentAPI } from '../services/api';

export const TrustLogs: React.FC = () => {
  const [trustLogs, setTrustLogs] = useState<TrustLog[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'allowed' | 'blocked'>('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [logsData, agentsData] = await Promise.all([
        agentAPI.getTrustLogs(),
        agentAPI.getAgents()
      ]);
      setTrustLogs(logsData);
      setAgents(agentsData);
    } catch (err) {
      setError('Failed to load trust logs');
      console.error('Trust logs loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getAgentName = (agentId: string) => {
    const agent = agents.find(a => a.id === agentId);
    return agent ? `${agent.name} (${agent.organization})` : 'Unknown Agent';
  };

  const getTrustScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const filteredLogs = trustLogs.filter(log => {
    if (filter === 'allowed') return log.trust_result.allowed;
    if (filter === 'blocked') return !log.trust_result.allowed;
    return true;
  });

  const stats = {
    total: trustLogs.length,
    allowed: trustLogs.filter(log => log.trust_result.allowed).length,
    blocked: trustLogs.filter(log => !log.trust_result.allowed).length,
    avgScore: trustLogs.length > 0 
      ? trustLogs.reduce((sum, log) => sum + log.trust_result.score, 0) / trustLogs.length 
      : 0
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <XCircleIcon className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Trust Verification Logs</h1>
        <p className="mt-2 text-gray-600">
          Monitor and audit all trust verification decisions between agents
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <ShieldCheckIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Verifications</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Allowed</p>
              <p className="text-2xl font-bold text-gray-900">{stats.allowed}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <XCircleIcon className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Blocked</p>
              <p className="text-2xl font-bold text-gray-900">{stats.blocked}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <ShieldCheckIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Trust Score</p>
              <p className={`text-2xl font-bold ${getTrustScoreColor(stats.avgScore)}`}>
                {(stats.avgScore * 100).toFixed(0)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-8">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Filter Logs</h2>
          
          <div className="flex items-center space-x-4">
            <FunnelIcon className="h-5 w-5 text-gray-400" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as 'all' | 'allowed' | 'blocked')}
              className="border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Verifications</option>
              <option value="allowed">Allowed Only</option>
              <option value="blocked">Blocked Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Logs Table */}
      <div className="card">
        {filteredLogs.length === 0 ? (
          <div className="text-center py-12">
            <ShieldCheckIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No trust logs yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Trust verifications will appear here when agents attempt to communicate.
            </p>
          </div>
        ) : (
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Source Agent
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Target Agent
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Result
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trust Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Reason
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Policies
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <ClockIcon className="h-4 w-4 text-gray-400 mr-2" />
                        {new Date(log.timestamp).toLocaleString()}
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="max-w-40 truncate" title={getAgentName(log.source_agent_id)}>
                        {getAgentName(log.source_agent_id)}
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="max-w-40 truncate" title={getAgentName(log.target_agent_id)}>
                        {getAgentName(log.target_agent_id)}
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      {log.trust_result.allowed ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <CheckCircleIcon className="h-3 w-3 mr-1" />
                          Allowed
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          <XCircleIcon className="h-3 w-3 mr-1" />
                          Blocked
                        </span>
                      )}
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`font-medium ${getTrustScoreColor(log.trust_result.score)}`}>
                        {(log.trust_result.score * 100).toFixed(0)}%
                      </span>
                    </td>
                    
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="max-w-48 truncate" title={log.trust_result.reason}>
                        {log.trust_result.reason}
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 text-sm text-gray-500">
                      <div className="space-y-1">
                        {log.trust_result.policies_passed.length > 0 && (
                          <div className="text-green-600">
                            ✓ {log.trust_result.policies_passed.join(', ')}
                          </div>
                        )}
                        {log.trust_result.policies_failed.length > 0 && (
                          <div className="text-red-600">
                            ✗ {log.trust_result.policies_failed.join(', ')}
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detailed Log View (Expandable) */}
      {filteredLogs.length > 0 && (
        <div className="card mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Latest Verification Details</h2>
          
          {filteredLogs.slice(0, 3).map((log) => (
            <details key={log.id} className="mb-4 border border-gray-200 rounded-lg">
              <summary className="p-4 cursor-pointer bg-gray-50 hover:bg-gray-100 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="font-medium">
                    {getAgentName(log.source_agent_id)} → {getAgentName(log.target_agent_id)}
                  </span>
                  <span className={`text-sm ${log.trust_result.allowed ? 'text-green-600' : 'text-red-600'}`}>
                    {log.trust_result.allowed ? 'ALLOWED' : 'BLOCKED'} ({(log.trust_result.score * 100).toFixed(0)}%)
                  </span>
                </div>
              </summary>
              
              <div className="p-4 bg-white">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Trust Result</h4>
                    <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                      {JSON.stringify(log.trust_result, null, 2)}
                    </pre>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Applied Policies</h4>
                    <div className="space-y-2">
                      {log.policies_applied.map((policy, index) => (
                        <div key={index} className="border border-gray-200 rounded p-2">
                          <div className="font-medium text-sm">{policy.name}</div>
                          <div className="text-xs text-gray-600">{policy.description}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </details>
          ))}
        </div>
      )}
    </div>
  );
};
