import React, { useState, useEffect } from 'react';
import { Search, Star, Users } from 'lucide-react';

import { API_BASE } from '../config';

interface Tool {
  id: number;
  name: string;
  slug: string;
  description: string;
  category: string;
  license: string;
  pricing_model: string;
  github_stars: number;
  github_forks: number;
  ai_summary: string;
  homepage_url: string;
  github_url: string;
}

const DiscoverPage: React.FC = () => {
  const [tools, setTools] = useState<Tool[]>([]);
  const [filteredTools, setFilteredTools] = useState<Tool[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedPricing, setSelectedPricing] = useState('all');
  const [sortBy, setSortBy] = useState('popularity');
  const [loading, setLoading] = useState(true);

  const categories = ['all', 'Container', 'Infrastructure', 'CI/CD', 'Monitoring'];
  const pricingModels = ['all', 'free', 'freemium', 'paid'];

  useEffect(() => {
    fetchTools();
  }, []);

  useEffect(() => {
    filterAndSortTools();
  }, [tools, searchTerm, selectedCategory, selectedPricing, sortBy]);

  const fetchTools = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/tools`);
      const data = await response.json();
      setTools(data);
    } catch (error) {
      console.error('Error fetching tools:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortTools = () => {
    let filtered = tools.filter(tool => {
      const matchesSearch = tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           tool.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || tool.category === selectedCategory;
      const matchesPricing = selectedPricing === 'all' || tool.pricing_model === selectedPricing;
      
      return matchesSearch && matchesCategory && matchesPricing;
    });

    // Sort tools
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'popularity':
          return b.github_stars - a.github_stars;
        case 'name':
          return a.name.localeCompare(b.name);
        case 'category':
          return a.category.localeCompare(b.category);
        default:
          return 0;
      }
    });

    setFilteredTools(filtered);
  };

  const getPricingColor = (pricing: string) => {
    switch (pricing) {
      case 'free': return 'bg-green-100 text-green-800';
      case 'freemium': return 'bg-blue-100 text-blue-800';
      case 'paid': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Container': return '📦';
      case 'Infrastructure': return '🏗️';
      case 'CI/CD': return '🔄';
      case 'Monitoring': return '📊';
      default: return '🛠️';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">
            🔍 Discover DevOps Tools
          </h1>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
            Explore our curated collection of DevOps and cloud engineering tools. 
            Find the perfect tools for your technology stack and workflow.
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 mb-12">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Search */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">Search Tools</label>
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Search by name or description..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                />
              </div>
            </div>

            {/* Category Filter */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full py-3 px-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
              >
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category === 'all' ? 'All Categories' : category}
                  </option>
                ))}
              </select>
            </div>

            {/* Pricing Filter */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">Pricing</label>
              <select
                value={selectedPricing}
                onChange={(e) => setSelectedPricing(e.target.value)}
                className="w-full py-3 px-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
              >
                {pricingModels.map(pricing => (
                  <option key={pricing} value={pricing}>
                    {pricing === 'all' ? 'All Pricing' : pricing.charAt(0).toUpperCase() + pricing.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Sort By */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full py-3 px-4 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
              >
                <option value="popularity">Popularity (Stars)</option>
                <option value="name">Name (A-Z)</option>
                <option value="category">Category</option>
              </select>
            </div>
          </div>

          {/* Results Count */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-gray-600">
              Showing <span className="font-semibold text-blue-600">{filteredTools.length}</span> of{' '}
              <span className="font-semibold">{tools.length}</span> tools
            </p>
          </div>
        </div>

        {/* Tools Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredTools.map((tool) => (
            <div key={tool.id} className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
              {/* Tool Header */}
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">{getCategoryIcon(tool.category)}</span>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">{tool.name}</h3>
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getPricingColor(tool.pricing_model)}`}>
                      {tool.pricing_model}
                    </span>
                  </div>
                </div>
              </div>

              {/* Tool Stats */}
              <div className="flex items-center space-x-6 mb-6">
                <div className="flex items-center space-x-2">
                  <Star className="text-yellow-500" size={18} />
                  <span className="text-sm font-medium text-gray-600">
                    {tool.github_stars.toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <Users className="text-blue-500" size={18} />
                  <span className="text-sm font-medium text-gray-600">
                    {tool.github_forks.toLocaleString()}
                  </span>
                </div>
                <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-lg text-xs font-medium">
                  {tool.category}
                </span>
              </div>

              {/* AI Summary */}
              <p className="text-gray-700 leading-relaxed mb-6 line-clamp-3">
                {tool.ai_summary}
              </p>

              {/* Action Buttons */}
              <div className="flex space-x-3">
                <a
                  href={`/tools/${tool.slug}`}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-xl font-semibold text-center hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
                >
                  View Details
                </a>
                <a
                  href={tool.homepage_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-3 border-2 border-gray-200 text-gray-700 rounded-xl font-semibold hover:border-blue-500 hover:text-blue-600 transition-all duration-200"
                >
                  Visit Site
                </a>
              </div>
            </div>
          ))}
        </div>

        {/* No Results */}
        {filteredTools.length === 0 && (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">No tools found</h3>
            <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DiscoverPage;
