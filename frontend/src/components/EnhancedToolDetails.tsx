import React from 'react';

interface EnhancedToolDetailsProps {
  tool: {
    name: string;
    description: string;
    category: string;
    license: string;
    pricing_model: string;
    github_stars: number;
    github_forks: number;
    homepage_url: string;
    github_url: string;
    ai_summary?: string;
  };
}

const EnhancedToolDetails: React.FC<EnhancedToolDetailsProps> = ({ tool }) => {
  const formatNumber = (num: number) => {
    return num.toLocaleString();
  };

  const getPricingBadgeColor = (pricing: string) => {
    switch (pricing.toLowerCase()) {
      case 'free': return 'bg-green-100 text-green-800';
      case 'freemium': return 'bg-blue-100 text-blue-800';
      case 'paid': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'container': return '📦';
      case 'ci/cd': return '🔄';
      case 'monitoring': return '📊';
      case 'infrastructure': return '🏗️';
      default: return '🛠️';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <span className="text-3xl">{getCategoryIcon(tool.category)}</span>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{tool.name}</h1>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-sm text-gray-600">{tool.category}</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPricingBadgeColor(tool.pricing_model)}`}>
                {tool.pricing_model}
              </span>
            </div>
          </div>
        </div>
        
        {/* GitHub Stats */}
        <div className="flex space-x-4 text-sm text-gray-600">
          <div className="flex items-center space-x-1">
            <span>⭐</span>
            <span>{formatNumber(tool.github_stars)}</span>
          </div>
          <div className="flex items-center space-x-1">
            <span>🍴</span>
            <span>{formatNumber(tool.github_forks)}</span>
          </div>
        </div>
      </div>

      {/* Quick Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
        <div>
          <h3 className="font-semibold text-gray-700 mb-1">License</h3>
          <p className="text-gray-600">{tool.license}</p>
        </div>
        <div>
          <h3 className="font-semibold text-gray-700 mb-1">GitHub Stars</h3>
          <p className="text-gray-600">{formatNumber(tool.github_stars)}</p>
        </div>
        <div>
          <h3 className="font-semibold text-gray-700 mb-1">Forks</h3>
          <p className="text-gray-600">{formatNumber(tool.github_forks)}</p>
        </div>
      </div>

      {/* Description */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-3">Overview</h2>
        <div className="prose max-w-none">
          <p className="text-gray-700 leading-relaxed whitespace-pre-line">
            {tool.description}
          </p>
        </div>
      </div>

      {/* AI Summary */}
      {tool.ai_summary && (
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3 flex items-center">
            <span className="mr-2">🤖</span>
            AI-Powered Analysis
          </h2>
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
            <p className="text-gray-700 leading-relaxed whitespace-pre-line">
              {tool.ai_summary}
            </p>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex space-x-4 pt-4 border-t border-gray-200">
        <a
          href={tool.homepage_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-center font-medium"
        >
          Visit Website
        </a>
        <a
          href={tool.github_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-900 transition-colors text-center font-medium"
        >
          View on GitHub
        </a>
        <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium">
          Add to Stack
        </button>
      </div>

      {/* Enhanced Features for Docker */}
      {tool.name.toLowerCase() === 'docker' && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Docker Ecosystem</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">🐳 Docker Hub</h3>
              <p className="text-blue-800 text-sm">World's largest container registry with millions of images</p>
            </div>
            <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-2">📝 Docker Compose</h3>
              <p className="text-green-800 text-sm">Define and run multi-container applications with YAML</p>
            </div>
            <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg">
              <h3 className="font-semibold text-purple-900 mb-2">🖥️ Docker Desktop</h3>
              <p className="text-purple-800 text-sm">Easy-to-use development environment for Mac and Windows</p>
            </div>
            <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg">
              <h3 className="font-semibold text-orange-900 mb-2">🐝 Docker Swarm</h3>
              <p className="text-orange-800 text-sm">Built-in orchestration for production deployments</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedToolDetails;
