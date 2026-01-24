import React, { useState, useEffect } from 'react';
import { ExternalLink, Star, GitBranch, Shield, Zap, Search } from 'lucide-react';
import { generateThumbnail, getTechIcon } from '../utils/thumbnails';

interface Tool {
  id: number;
  name: string;
  slug: string;
  description: string;
  homepage_url?: string;
  github_url?: string;
  category: string;
  license?: string;
  pricing_model: string;
  github_stars: number;
  github_forks: number;
  ai_summary?: string;
  created_at: string;
  updated_at?: string;
}

const ToolsPage: React.FC = () => {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  useEffect(() => {
    fetchTools();
  }, []);

  const fetchTools = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/tools');
      const data = await response.json();
      setTools(data);
    } catch (error) {
      console.error('Error fetching tools:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = ['All', ...Array.from(new Set(tools.map(tool => tool.category)))];

  const filteredTools = tools.filter(tool => {
    const matchesSearch = tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tool.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || tool.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getPricingColor = (pricing: string) => {
    switch (pricing.toLowerCase()) {
      case 'free': return 'bg-green-100 text-green-800';
      case 'freemium': return 'bg-blue-100 text-blue-800';
      case 'paid': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading DevOps tools...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <style>{`
        .line-clamp-3 {
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">DevOps Tools Arsenal</h1>
          <p className="text-xl mb-8 max-w-3xl mx-auto opacity-90">
            Comprehensive collection of {tools.length} production-ready DevOps tools for modern infrastructure,
            CI/CD, monitoring, security, and cloud-native development.
          </p>
          <div className="flex justify-center space-x-6 text-sm">
            <div className="flex items-center">
              <Shield className="w-5 h-5 mr-2" />
              <span>Enterprise Grade</span>
            </div>
            <div className="flex items-center">
              <Zap className="w-5 h-5 mr-2" />
              <span>Production Ready</span>
            </div>
            <div className="flex items-center">
              <GitBranch className="w-5 h-5 mr-2" />
              <span>Open Source</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Search and Filter */}
        <div className="mb-8 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search tools by name or description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex flex-wrap gap-2">
            {categories.map(category => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${selectedCategory === category
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                  }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Tools Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTools.map((tool) => (
            <div key={tool.id} className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group">
              {/* Thumbnail */}
              <div className="relative h-48 overflow-hidden">
                <img
                  src={generateThumbnail(tool.name)}
                  alt={tool.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute top-4 left-4">
                  <span className="text-3xl">{getTechIcon(tool.name)}</span>
                </div>
                <div className="absolute top-4 right-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPricingColor(tool.pricing_model)}`}>
                    {tool.pricing_model}
                  </span>
                </div>
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
                  <span className="text-white text-sm font-medium">{tool.category}</span>
                </div>
              </div>

              {/* Content */}
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                    {tool.name}
                  </h3>
                  <div className="flex items-center text-yellow-500 ml-2">
                    <Star size={16} className="fill-current" />
                    <span className="ml-1 text-sm text-gray-600">{tool.github_stars.toLocaleString()}</span>
                  </div>
                </div>

                <p className="text-gray-600 text-sm leading-relaxed mb-4 line-clamp-3">
                  {tool.ai_summary || tool.description}
                </p>

                <div className="flex items-center justify-between">
                  <div className="flex space-x-2">
                    {tool.homepage_url && (
                      <a
                        href={tool.homepage_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-blue-600 hover:text-blue-800 text-sm"
                      >
                        <ExternalLink size={14} className="mr-1" />
                        Website
                      </a>
                    )}
                    {tool.github_url && (
                      <a
                        href={tool.github_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-gray-600 hover:text-gray-800 text-sm"
                      >
                        <GitBranch size={14} className="mr-1" />
                        GitHub
                      </a>
                    )}
                  </div>
                  {tool.license && (
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      {tool.license}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredTools.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No tools found matching your criteria.</p>
          </div>
        )}

        {/* Stats */}
        <div className="mt-12 bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Platform Statistics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-3xl font-bold text-blue-600">{tools.length}</div>
              <div className="text-gray-600">Total Tools</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-600">{categories.length - 1}</div>
              <div className="text-gray-600">Categories</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-purple-600">
                {tools.reduce((sum, tool) => sum + tool.github_stars, 0).toLocaleString()}
              </div>
              <div className="text-gray-600">Total Stars</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-orange-600">
                {tools.filter(tool => tool.pricing_model === 'free').length}
              </div>
              <div className="text-gray-600">Free Tools</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ToolsPage;
