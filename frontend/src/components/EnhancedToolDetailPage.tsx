import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Star, Github, ExternalLink, Users, Award, Zap, Shield, TrendingUp, BookOpen, Code, Heart } from 'lucide-react';
import ReviewsSection from './ReviewsSection';

import { API_BASE } from '../config';

interface Tool {
  id: number;
  name: string;
  slug: string;
  description: string;
  homepage_url: string;
  github_url: string;
  category: string;
  license: string;
  pricing_model: string;
  github_stars: number;
  github_forks: number;
  ai_summary: string;
  health_score?: number;
  created_at: string;
}

const EnhancedToolDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [tool, setTool] = useState<Tool | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (slug) {
      fetchTool();
    }
  }, [slug]);

  const fetchTool = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/tools`);
      const tools = await response.json();
      const foundTool = tools.find((t: Tool) => t.slug === slug);
      setTool(foundTool || null);
    } catch (error) {
      console.error('Error fetching tool:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPricingColor = (pricing: string) => {
    switch (pricing) {
      case 'free': return 'bg-green-100 text-green-800 border-green-200';
      case 'freemium': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'paid': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
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

  const parseDescription = (description: string) => {
    // Split by ** to get sections
    const parts = description.split('**');
    const sections = [];
    
    // First part is usually the main description
    const mainDescription = parts[0].trim();
    
    // Process remaining parts as sections
    for (let i = 1; i < parts.length; i += 2) {
      if (i + 1 < parts.length) {
        const title = parts[i].replace(/:/g, '').trim();
        const content = parts[i + 1].trim();
        
        // Skip empty sections
        if (title && content) {
          sections.push({ 
            title, 
            content,
            items: content.split('•').filter(item => item.trim()).map(item => item.trim())
          });
        }
      }
    }
    
    return { mainDescription, sections };
  };

  const getFeatureIcon = (title: string) => {
    const iconMap: { [key: string]: string } = {
      'Core Features': '⚡',
      'Key Features': '🔑',
      'Advanced Capabilities': '🚀',
      'Enterprise Features': '🏢',
      'Production Features': '🏭',
      'Core Architecture': '🏗️',
      'Architecture': '🏗️',
      'Integration Ecosystem': '🔗',
      'Use Cases': '💼',
      'Performance': '📈',
      'Security': '🔒',
      'Monitoring': '📊',
      'Deployment': '🚀',
      'Scalability': '📊'
    };
    
    // Find matching icon or use default
    for (const [key, icon] of Object.entries(iconMap)) {
      if (title.toLowerCase().includes(key.toLowerCase())) {
        return icon;
      }
    }
    return '🛠️';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading tool details...</p>
        </div>
      </div>
    );
  }

  if (!tool) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🔍</div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Tool Not Found</h2>
          <p className="text-gray-600">The tool you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  const sections = parseDescription(tool.description);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden mb-12">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-12 py-16 text-white">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-4 mb-6">
                  <span className="text-6xl">{getCategoryIcon(tool.category)}</span>
                  <div>
                    <h1 className="text-5xl font-bold mb-2">{tool.name}</h1>
                    <p className="text-xl text-blue-100">{tool.ai_summary}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-6 mb-8">
                  <div className="flex items-center space-x-2">
                    <Star className="text-yellow-300" size={24} />
                    <span className="text-2xl font-bold">{tool.github_stars.toLocaleString()}</span>
                    <span className="text-blue-100">stars</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Users className="text-blue-200" size={24} />
                    <span className="text-2xl font-bold">{tool.github_forks.toLocaleString()}</span>
                    <span className="text-blue-100">forks</span>
                  </div>
                  <span className={`px-4 py-2 rounded-full border-2 font-semibold ${getPricingColor(tool.pricing_model)} bg-white`}>
                    {tool.pricing_model.toUpperCase()}
                  </span>
                </div>

                <div className="flex space-x-4">
                  <a
                    href={tool.homepage_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-white text-blue-600 px-8 py-4 rounded-xl font-bold hover:bg-blue-50 transition-all duration-200 flex items-center space-x-2 shadow-lg"
                  >
                    <ExternalLink size={20} />
                    <span>Visit Website</span>
                  </a>
                  <a
                    href={tool.github_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-gray-800 text-white px-8 py-4 rounded-xl font-bold hover:bg-gray-700 transition-all duration-200 flex items-center space-x-2 shadow-lg"
                  >
                    <Github size={20} />
                    <span>View on GitHub</span>
                  </a>
                </div>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-12">
              {[
                { id: 'overview', label: 'Overview', icon: BookOpen },
                { id: 'features', label: 'Features', icon: Zap },
                { id: 'architecture', label: 'Architecture', icon: Code },
                { id: 'reviews', label: 'Reviews', icon: Heart }
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id)}
                  className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium transition-all duration-200 ${
                    activeTab === id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon size={20} />
                  <span>{label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="px-12 py-10">
            {activeTab === 'overview' && (
              <div className="space-y-8">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-6">About {tool.name}</h2>
                  <div className="prose prose-lg max-w-none">
                    <p className="text-gray-700 leading-relaxed text-lg">
                      {sections.mainDescription}
                    </p>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-6 text-center hover:shadow-lg transition-all duration-200">
                    <Award className="text-blue-600 mx-auto mb-3" size={32} />
                    <div className="text-2xl font-bold text-blue-900">{tool.category}</div>
                    <div className="text-blue-700">Category</div>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-6 text-center hover:shadow-lg transition-all duration-200">
                    <Shield className="text-green-600 mx-auto mb-3" size={32} />
                    <div className="text-2xl font-bold text-green-900">{tool.license}</div>
                    <div className="text-green-700">License</div>
                  </div>
                  <div className="bg-gradient-to-br from-purple-50 to-violet-50 border-2 border-purple-200 rounded-xl p-6 text-center hover:shadow-lg transition-all duration-200">
                    <TrendingUp className="text-purple-600 mx-auto mb-3" size={32} />
                    <div className="text-2xl font-bold text-purple-900">{tool.github_stars.toLocaleString()}</div>
                    <div className="text-purple-700">GitHub Stars</div>
                  </div>
                  <div className="bg-gradient-to-br from-orange-50 to-red-50 border-2 border-orange-200 rounded-xl p-6 text-center hover:shadow-lg transition-all duration-200">
                    <Users className="text-orange-600 mx-auto mb-3" size={32} />
                    <div className="text-2xl font-bold text-orange-900">{tool.github_forks.toLocaleString()}</div>
                    <div className="text-orange-700">Forks</div>
                  </div>
                  <div className="bg-gradient-to-br from-teal-50 to-cyan-50 border-2 border-teal-200 rounded-xl p-6 text-center hover:shadow-lg transition-all duration-200">
                    <Heart className="text-teal-600 mx-auto mb-3" size={32} />
                    <div className="text-2xl font-bold text-teal-900">{tool.health_score || 'N/A'}{tool.health_score ? '/100' : ''}</div>
                    <div className="text-teal-700">Health Score</div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'features' && (
              <div className="space-y-10">
                <div className="text-center mb-12">
                  <h2 className="text-4xl font-bold text-gray-900 mb-4">🔑 Key Features & Capabilities</h2>
                  <p className="text-xl text-gray-600">Discover what makes {tool.name} powerful and unique</p>
                </div>
                
                <div className="space-y-8">
                  {sections.sections.length > 0 ? (
                    sections.sections.map((section, index) => {
                      const colors = [
                        'from-blue-50 to-cyan-50 border-blue-200 text-blue-900',
                        'from-green-50 to-emerald-50 border-green-200 text-green-900',
                        'from-purple-50 to-violet-50 border-purple-200 text-purple-900',
                        'from-orange-50 to-red-50 border-orange-200 text-orange-900',
                        'from-pink-50 to-rose-50 border-pink-200 text-pink-900',
                        'from-indigo-50 to-blue-50 border-indigo-200 text-indigo-900'
                      ];
                      const colorClass = colors[index % colors.length];
                      
                      return (
                        <div key={index} className={`bg-gradient-to-br ${colorClass} border-2 rounded-2xl p-8 hover:shadow-xl transition-all duration-300`}>
                          <div className="flex items-center mb-6">
                            <span className="text-4xl mr-4">{getFeatureIcon(section.title)}</span>
                            <h3 className="text-3xl font-bold">{section.title}</h3>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {section.items.map((item, idx) => {
                              // Parse feature items that might have bold parts
                              const parts = item.split('**');
                              return (
                                <div key={idx} className="bg-white bg-opacity-70 rounded-xl p-4 hover:bg-opacity-90 transition-all duration-200">
                                  <div className="flex items-start space-x-3">
                                    <span className="text-blue-500 mt-1 text-lg">•</span>
                                    <div className="text-gray-800 leading-relaxed">
                                      {parts.map((part, partIdx) => 
                                        partIdx % 2 === 1 ? 
                                          <strong key={partIdx} className="font-bold text-gray-900">{part}</strong> : 
                                          <span key={partIdx}>{part}</span>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    // Fallback: Show all content as features if no structured sections found
                    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-blue-200 rounded-2xl p-8">
                      <div className="flex items-center mb-6">
                        <span className="text-4xl mr-4">🔑</span>
                        <h3 className="text-3xl font-bold text-blue-900">Key Features</h3>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {tool.description.split('•').filter(item => item.trim()).map((item, idx) => (
                          <div key={idx} className="bg-white bg-opacity-70 rounded-xl p-4 hover:bg-opacity-90 transition-all duration-200">
                            <div className="flex items-start space-x-3">
                              <span className="text-blue-500 mt-1 text-lg">•</span>
                              <div className="text-gray-800 leading-relaxed">
                                {item.trim()}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'architecture' && (
              <div className="space-y-10">
                <div className="text-center mb-12">
                  <h2 className="text-4xl font-bold text-gray-900 mb-4">🏗️ Technical Architecture</h2>
                  <p className="text-xl text-gray-600">Deep dive into {tool.name}'s technical implementation</p>
                </div>
                
                <div className="space-y-8">
                  {sections.sections.length > 0 ? (
                    sections.sections.map((section, index) => (
                      <div key={index} className="bg-gradient-to-r from-gray-50 to-blue-50 border-2 border-gray-200 rounded-2xl p-8 hover:shadow-xl transition-all duration-300">
                        <div className="flex items-center mb-6">
                          <span className="text-4xl mr-4">{getFeatureIcon(section.title)}</span>
                          <h3 className="text-3xl font-bold text-gray-900">{section.title}</h3>
                        </div>
                        
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          {section.items.map((item, idx) => {
                            const parts = item.split('**');
                            return (
                              <div key={idx} className="bg-white border-2 border-gray-100 rounded-xl p-6 hover:border-blue-300 hover:shadow-lg transition-all duration-200">
                                <div className="text-gray-800 leading-relaxed">
                                  {parts.map((part, partIdx) => 
                                    partIdx % 2 === 1 ? 
                                      <strong key={partIdx} className="font-bold text-blue-900 block mb-2">{part}:</strong> : 
                                      <span key={partIdx}>{part}</span>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ))
                  ) : (
                    // Fallback: Show description content
                    <div className="bg-gradient-to-r from-gray-50 to-blue-50 border-2 border-gray-200 rounded-2xl p-8">
                      <div className="flex items-center mb-6">
                        <span className="text-4xl mr-4">🏗️</span>
                        <h3 className="text-3xl font-bold text-gray-900">Technical Details</h3>
                      </div>
                      
                      <div className="prose prose-lg max-w-none">
                        <p className="text-gray-700 leading-relaxed">
                          {sections.mainDescription}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'reviews' && (
              <ReviewsSection toolId={tool.id} toolName={tool.name} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedToolDetailPage;
