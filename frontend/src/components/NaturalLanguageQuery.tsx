import React, { useState } from 'react';
import { Search, Sparkles, Star, ExternalLink } from 'lucide-react';

import { API_BASE } from '../config';

interface SearchResult {
  name: string;
  id: number;
  slug: string;
  relevance_score: number;
  why_recommended: string;
  use_case: string;
  category: string;
  github_stars: number;
  license: string;
  pricing_model: string;
  homepage_url: string;
}

interface SearchResponse {
  recommended_tools: SearchResult[];
  search_summary: string;
  alternative_suggestions: string[];
  learning_path?: string;
}

const NaturalLanguageQuery: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE}/api/ai/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim() })
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError('Failed to search tools. Please try again.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
  };

  const getPricingColor = (pricing: string) => {
    switch (pricing) {
      case 'free': return 'bg-green-100 text-green-800';
      case 'freemium': return 'bg-blue-100 text-blue-800';
      case 'paid': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">
            🤖 AI-Powered Tool Search
          </h1>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
            Ask in natural language and get intelligent tool recommendations powered by comprehensive data analysis
          </p>
        </div>

        {/* Search Interface */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 mb-8">
          <div className="flex space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={24} />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="e.g., 'I need a tool for container orchestration' or 'What's the best CI/CD tool for small teams?'"
                className="w-full pl-12 pr-4 py-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 text-lg"
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={loading || !query.trim()}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 shadow-lg hover:shadow-xl transition-all duration-200"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Sparkles size={24} />
                  <span>Search</span>
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="mt-4 bg-red-50 border-2 border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
        </div>

        {/* Example Queries */}
        {!results && (
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">💡 Try These Example Queries</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                "I need a tool for container orchestration",
                "What's the best monitoring solution?",
                "CI/CD tool for small development teams",
                "Infrastructure as code for AWS",
                "Free tools for DevOps automation",
                "Best practices for microservices deployment"
              ].map((example, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(example)}
                  className="text-left p-4 border-2 border-gray-200 rounded-xl hover:border-blue-300 hover:bg-blue-50 transition-all duration-200"
                >
                  <span className="text-blue-600 font-medium">{example}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Search Results */}
        {results && (
          <div className="space-y-8">
            {/* Summary */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">🎯 Search Results</h2>
              <p className="text-lg text-gray-700 leading-relaxed">{results.search_summary}</p>
              {results.learning_path && (
                <div className="mt-4 p-4 bg-blue-50 border-2 border-blue-200 rounded-xl">
                  <h4 className="font-semibold text-blue-900 mb-2">📚 Recommended Learning Path:</h4>
                  <p className="text-blue-800">{results.learning_path}</p>
                </div>
              )}
            </div>

            {/* Tool Recommendations */}
            <div className="space-y-6">
              {results.recommended_tools.map((tool, index) => (
                <div key={tool.id} className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 hover:shadow-2xl transition-all duration-300">
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-2xl font-bold text-gray-900">{tool.name}</h3>
                        <div className="flex items-center space-x-2">
                          <div className={`w-3 h-3 rounded-full ${getRelevanceColor(tool.relevance_score)}`}></div>
                          <span className="text-sm font-medium text-gray-600">{tool.relevance_score}% match</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-4 mb-4">
                        <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm font-medium">
                          {tool.category}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPricingColor(tool.pricing_model)}`}>
                          {tool.pricing_model}
                        </span>
                        <div className="flex items-center space-x-1">
                          <Star className="text-yellow-500" size={16} />
                          <span className="text-sm text-gray-600">{tool.github_stars.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-3xl font-bold text-blue-600">#{index + 1}</div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">🎯 Why Recommended:</h4>
                      <p className="text-gray-700">{tool.why_recommended}</p>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">💼 Use Case:</h4>
                      <p className="text-gray-700">{tool.use_case}</p>
                    </div>
                  </div>

                  <div className="flex space-x-4 mt-6">
                    <a
                      href={`/tools/${tool.slug}`}
                      className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
                    >
                      View Details
                    </a>
                    <a
                      href={tool.homepage_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="border-2 border-gray-200 text-gray-700 px-6 py-3 rounded-xl font-semibold hover:border-blue-500 hover:text-blue-600 transition-all duration-200 flex items-center space-x-2"
                    >
                      <ExternalLink size={18} />
                      <span>Visit Site</span>
                    </a>
                  </div>
                </div>
              ))}
            </div>

            {/* Alternative Suggestions */}
            {results.alternative_suggestions && results.alternative_suggestions.length > 0 && (
              <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">💡 Alternative Suggestions</h3>
                <div className="space-y-3">
                  {results.alternative_suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="block w-full text-left p-4 border-2 border-gray-200 rounded-xl hover:border-blue-300 hover:bg-blue-50 transition-all duration-200"
                    >
                      <span className="text-blue-600 font-medium">{suggestion}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* New Search */}
            <div className="text-center">
              <button
                onClick={() => {
                  setResults(null);
                  setQuery('');
                }}
                className="bg-gray-500 text-white px-8 py-3 rounded-xl font-semibold hover:bg-gray-600 transition-all duration-200"
              >
                New Search
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NaturalLanguageQuery;
