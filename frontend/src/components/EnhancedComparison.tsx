import React, { useState } from 'react';
import { Search, X, Zap, AlertCircle } from 'lucide-react';

import { API_BASE } from '../config';

interface ComparisonResult {
  tool1: string;
  tool2: string;
  detailed_analysis: {
    overview: string;
    technical_comparison: {
      architecture: string;
      performance: string;
      scalability: string;
      security: string;
    };
    business_analysis: {
      cost_analysis: string;
      learning_curve: string;
      community_support: string;
      enterprise_readiness: string;
    };
    use_case_scenarios: {
      startup: string;
      enterprise: string;
      specific_industries: string;
    };
    pros_cons: {
      tool1_pros: string[];
      tool1_cons: string[];
      tool2_pros: string[];
      tool2_cons: string[];
    };
    decision_matrix: {
      criteria: string;
      tool1_score: number;
      tool2_score: number;
      reasoning: string;
    }[];
    final_recommendation: string;
  };
}

const EnhancedComparison: React.FC = () => {
  const [tool1, setTool1] = useState('');
  const [tool2, setTool2] = useState('');
  const [loading, setLoading] = useState(false);
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [error, setError] = useState('');

  const handleCompare = async () => {
    if (!tool1.trim() || !tool2.trim()) {
      setError('Please enter both tool names');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE}/api/ai/enhanced-compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          tool1: tool1.trim(), 
          tool2: tool2.trim() 
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate comparison');
      }

      const result = await response.json();
      setComparison(result);
    } catch (err) {
      setError('Failed to generate comparison. Please try again.');
      console.error('Comparison error:', err);
    } finally {
      setLoading(false);
    }
  };

  const clearComparison = () => {
    setComparison(null);
    setTool1('');
    setTool2('');
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">
            🎯 Enterprise Tool Comparison
          </h1>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
            Get detailed, AI-powered analysis to help engineering managers and decision-makers 
            choose the right tools for their organization
          </p>
        </div>

        {/* Search Interface */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 mb-12">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                First Tool
              </label>
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="e.g., Docker, Kubernetes, Jenkins..."
                  value={tool1}
                  onChange={(e) => setTool1(e.target.value)}
                  className="w-full pl-12 pr-4 py-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 text-lg"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Second Tool
              </label>
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="e.g., Podman, OpenShift, GitHub Actions..."
                  value={tool2}
                  onChange={(e) => setTool2(e.target.value)}
                  className="w-full pl-12 pr-4 py-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 text-lg"
                />
              </div>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border-2 border-red-200 text-red-700 px-6 py-4 rounded-xl mb-6 flex items-center">
              <AlertCircle size={24} className="mr-3" />
              <span className="font-medium">{error}</span>
            </div>
          )}

          <div className="flex justify-center space-x-6">
            <button
              onClick={handleCompare}
              disabled={loading || !tool1.trim() || !tool2.trim()}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-10 py-4 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center shadow-lg hover:shadow-xl transition-all duration-200 text-lg"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <Zap size={24} className="mr-3" />
                  Generate Detailed Analysis
                </>
              )}
            </button>

            {comparison && (
              <button
                onClick={clearComparison}
                className="bg-gray-500 text-white px-8 py-4 rounded-xl font-semibold hover:bg-gray-600 flex items-center shadow-lg hover:shadow-xl transition-all duration-200 text-lg"
              >
                <X size={24} className="mr-3" />
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Comparison Results */}
        {comparison && (
          <div className="space-y-10">
            {/* Overview */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-10">
              <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center">
                📊 Executive Summary
              </h2>
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-8 rounded-xl border border-blue-100">
                <div className="text-blue-900 leading-relaxed text-lg space-y-4">
                  {(comparison.detailed_analysis.overview || '').split('\n').map((paragraph, idx) => (
                    <p key={idx} className="mb-3">{paragraph}</p>
                  ))}
                </div>
              </div>
            </div>

            {/* Technical Comparison */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-10">
              <h2 className="text-3xl font-bold text-gray-900 mb-8 flex items-center">
                ⚙️ Technical Analysis
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {Object.entries(comparison.detailed_analysis.technical_comparison).map(([key, value], index) => {
                  const icons = {
                    architecture: '🏗️',
                    performance: '⚡',
                    scalability: '📈',
                    security: '🔒'
                  };
                  const colorClasses = [
                    { bg: 'bg-gradient-to-br from-green-50 to-emerald-50', border: 'border-green-200', text: 'text-green-800', content: 'text-green-700' },
                    { bg: 'bg-gradient-to-br from-blue-50 to-cyan-50', border: 'border-blue-200', text: 'text-blue-800', content: 'text-blue-700' },
                    { bg: 'bg-gradient-to-br from-purple-50 to-violet-50', border: 'border-purple-200', text: 'text-purple-800', content: 'text-purple-700' },
                    { bg: 'bg-gradient-to-br from-red-50 to-rose-50', border: 'border-red-200', text: 'text-red-800', content: 'text-red-700' }
                  ];
                  const colors = colorClasses[index % colorClasses.length];
                  
                  return (
                    <div key={key} className={`${colors.bg} ${colors.border} border-2 p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200`}>
                      <h3 className={`font-bold ${colors.text} mb-4 flex items-center capitalize text-xl`}>
                        <span className="text-2xl mr-3">{icons[key as keyof typeof icons]}</span>
                        {key}
                      </h3>
                      <div className="space-y-3">
                        {((value as string) || '').split('\n\n').map((tool, idx) => {
                          const parts = tool.split('**');
                          return (
                            <div key={idx} className={`${colors.content} space-y-2`}>
                              {parts.map((part, i) => {
                                if (i % 2 === 1) {
                                  return <strong key={i} className="font-bold block mb-2 text-lg">{part}:</strong>;
                                } else {
                                  return part.split('\n').map((line, lineIdx) => (
                                    <div key={`${i}-${lineIdx}`} className="text-base leading-relaxed mb-2">
                                      {line}
                                    </div>
                                  ));
                                }
                              })}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Business Analysis */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-10">
              <h2 className="text-3xl font-bold text-gray-900 mb-8 flex items-center">
                💼 Business Impact Analysis
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {Object.entries(comparison.detailed_analysis.business_analysis).map(([key, value], index) => {
                  const icons = {
                    cost_analysis: '💰',
                    learning_curve: '📚',
                    community_support: '👥',
                    enterprise_readiness: '🏢'
                  };
                  const colorClasses = [
                    { bg: 'bg-gradient-to-br from-yellow-50 to-amber-50', border: 'border-yellow-200', text: 'text-yellow-800', content: 'text-yellow-700' },
                    { bg: 'bg-gradient-to-br from-indigo-50 to-blue-50', border: 'border-indigo-200', text: 'text-indigo-800', content: 'text-indigo-700' },
                    { bg: 'bg-gradient-to-br from-pink-50 to-rose-50', border: 'border-pink-200', text: 'text-pink-800', content: 'text-pink-700' },
                    { bg: 'bg-gradient-to-br from-teal-50 to-cyan-50', border: 'border-teal-200', text: 'text-teal-800', content: 'text-teal-700' }
                  ];
                  const colors = colorClasses[index % colorClasses.length];
                  
                  return (
                    <div key={key} className={`${colors.bg} ${colors.border} border-2 p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200`}>
                      <h3 className={`font-bold ${colors.text} mb-4 flex items-center text-xl`}>
                        <span className="text-2xl mr-3">{icons[key as keyof typeof icons]}</span>
                        {key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                      </h3>
                      <div className="space-y-3">
                        {((value as string) || '').split('\n\n').map((section, idx) => {
                          const parts = section.split('**');
                          return (
                            <div key={idx} className={`${colors.content} space-y-2`}>
                              {parts.map((part, i) => {
                                if (i % 2 === 1) {
                                  return <strong key={i} className="font-bold block mb-2 text-lg">{part}:</strong>;
                                } else {
                                  return part.split('\n').map((line, lineIdx) => (
                                    <div key={`${i}-${lineIdx}`} className="text-base leading-relaxed mb-2">
                                      {line}
                                    </div>
                                  ));
                                }
                              })}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Use Case Scenarios */}
            <div className="bg-white rounded-lg shadow-sm p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">🎯 Use Case Scenarios</h2>
              <div className="space-y-6">
                {Object.entries(comparison.detailed_analysis.use_case_scenarios).map(([key, value]) => {
                  const icons = {
                    startup: '🚀',
                    enterprise: '🏢',
                    specific_industries: '🏭'
                  };
                  const gradients = {
                    startup: 'from-green-50 to-blue-50',
                    enterprise: 'from-blue-50 to-purple-50',
                    specific_industries: 'from-purple-50 to-pink-50'
                  };
                  
                  return (
                    <div key={key} className={`bg-gradient-to-r ${gradients[key as keyof typeof gradients]} p-6 rounded-lg`}>
                      <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
                        {icons[key as keyof typeof icons]} {key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                      </h3>
                      <div className="text-gray-700 space-y-2">
                        {((value as string) || '').split('**').map((part, i) => 
                          i % 2 === 1 ? 
                            <strong key={i} className="font-bold">{part}</strong> : 
                            <span key={i}>{part}</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Pros and Cons */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-10">
              <h2 className="text-3xl font-bold text-gray-900 mb-8">⚖️ Pros & Cons Analysis</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                <div>
                  <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">{comparison.tool1}</h3>
                  <div className="space-y-6">
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 p-6 rounded-xl shadow-lg">
                      <h4 className="font-bold text-green-800 mb-4 text-xl flex items-center">
                        <span className="text-2xl mr-2">✅</span> Advantages
                      </h4>
                      <ul className="space-y-2">
                        {comparison.detailed_analysis.pros_cons.tool1_pros.map((pro, index) => (
                          <li key={index} className="text-green-700 flex items-start">
                            <span className="text-green-500 mr-2 mt-1">•</span>
                            <span className="text-base leading-relaxed">{pro}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="bg-gradient-to-br from-red-50 to-rose-50 border-2 border-red-200 p-6 rounded-xl shadow-lg">
                      <h4 className="font-bold text-red-800 mb-4 text-xl flex items-center">
                        <span className="text-2xl mr-2">❌</span> Limitations
                      </h4>
                      <ul className="space-y-2">
                        {comparison.detailed_analysis.pros_cons.tool1_cons.map((con, index) => (
                          <li key={index} className="text-red-700 flex items-start">
                            <span className="text-red-500 mr-2 mt-1">•</span>
                            <span className="text-base leading-relaxed">{con}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">{comparison.tool2}</h3>
                  <div className="space-y-6">
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 p-6 rounded-xl shadow-lg">
                      <h4 className="font-bold text-green-800 mb-4 text-xl flex items-center">
                        <span className="text-2xl mr-2">✅</span> Advantages
                      </h4>
                      <ul className="space-y-2">
                        {comparison.detailed_analysis.pros_cons.tool2_pros.map((pro, index) => (
                          <li key={index} className="text-green-700 flex items-start">
                            <span className="text-green-500 mr-2 mt-1">•</span>
                            <span className="text-base leading-relaxed">{pro}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="bg-gradient-to-br from-red-50 to-rose-50 border-2 border-red-200 p-6 rounded-xl shadow-lg">
                      <h4 className="font-bold text-red-800 mb-4 text-xl flex items-center">
                        <span className="text-2xl mr-2">❌</span> Limitations
                      </h4>
                      <ul className="space-y-2">
                        {comparison.detailed_analysis.pros_cons.tool2_cons.map((con, index) => (
                          <li key={index} className="text-red-700 flex items-start">
                            <span className="text-red-500 mr-2 mt-1">•</span>
                            <span className="text-base leading-relaxed">{con}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Decision Matrix */}
            <div className="bg-white rounded-lg shadow-sm p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                📊 Decision Matrix
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border border-gray-200 px-4 py-3 text-left font-semibold">Criteria</th>
                      <th className="border border-gray-200 px-4 py-3 text-center font-semibold">{comparison.tool1}</th>
                      <th className="border border-gray-200 px-4 py-3 text-center font-semibold">{comparison.tool2}</th>
                      <th className="border border-gray-200 px-4 py-3 text-left font-semibold">Analysis</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparison.detailed_analysis.decision_matrix.map((item, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="border border-gray-200 px-4 py-3 font-medium">{item.criteria}</td>
                        <td className="border border-gray-200 px-4 py-3 text-center">
                          <span className={`inline-block w-8 h-8 rounded-full text-white font-bold text-sm flex items-center justify-center ${
                            item.tool1_score >= 8 ? 'bg-green-500' : 
                            item.tool1_score >= 6 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}>
                            {item.tool1_score}
                          </span>
                        </td>
                        <td className="border border-gray-200 px-4 py-3 text-center">
                          <span className={`inline-block w-8 h-8 rounded-full text-white font-bold text-sm flex items-center justify-center ${
                            item.tool2_score >= 8 ? 'bg-green-500' : 
                            item.tool2_score >= 6 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}>
                            {item.tool2_score}
                          </span>
                        </td>
                        <td className="border border-gray-200 px-4 py-3 text-sm text-gray-700">{item.reasoning}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Final Recommendation */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg shadow-sm p-8">
              <h2 className="text-2xl font-bold mb-4 flex items-center">
                🎯 Final Recommendation
              </h2>
              <div className="bg-white bg-opacity-10 p-6 rounded-lg space-y-4">
                {(comparison.detailed_analysis.final_recommendation || '').split(/\n\s*\n/).filter(paragraph => paragraph.trim()).map((paragraph, idx) => {
                  const parts = paragraph.split('**');
                  return (
                    <div key={idx} className="leading-relaxed text-lg mb-4">
                      {parts.map((part, i) => 
                        i % 2 === 1 ? 
                          <strong key={i} className="font-bold">{part}</strong> : 
                          <span key={i}>{part}</span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedComparison;
