import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, LineChart, Line, ResponsiveContainer } from 'recharts';
import { TrendingUp, Users, Star, GitFork, Award, Activity } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

interface AnalyticsData {
  overview: {
    total_tools: number;
    total_stars: number;
    total_forks: number;
    avg_stars: number;
    categories: number;
    licenses: number;
  };
  category_distribution: Array<{name: string; count: number; percentage: number}>;
  pricing_distribution: Array<{name: string; count: number; percentage: number}>;
  license_distribution: Array<{name: string; count: number; percentage: number}>;
  top_tools: Array<{
    name: string;
    category: string;
    stars: number;
    forks: number;
    license: string;
    pricing: string;
  }>;
  growth_trends: Array<{month: string; tools: number; stars: number}>;
  insights: string[];
}

const AnalyticsDashboard: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/analytics/overview`);
      if (!response.ok) {
        throw new Error('Failed to fetch analytics');
      }
      const analyticsData = await response.json();
      setData(analyticsData);
    } catch (err) {
      setError('Unable to load analytics data');
      console.error('Analytics error:', err);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">📊</div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Analytics Unavailable</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchAnalytics}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">
            📊 Platform Analytics
          </h1>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
            Comprehensive insights into the DevOps tools ecosystem and community engagement
          </p>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-12">
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Tools</p>
                <p className="text-3xl font-bold text-blue-600">{data.overview.total_tools}</p>
              </div>
              <Award className="text-blue-500" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Stars</p>
                <p className="text-3xl font-bold text-yellow-600">{data.overview.total_stars.toLocaleString()}</p>
              </div>
              <Star className="text-yellow-500" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Forks</p>
                <p className="text-3xl font-bold text-green-600">{data.overview.total_forks.toLocaleString()}</p>
              </div>
              <GitFork className="text-green-500" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Stars</p>
                <p className="text-3xl font-bold text-purple-600">{data.overview.avg_stars.toLocaleString()}</p>
              </div>
              <TrendingUp className="text-purple-500" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Categories</p>
                <p className="text-3xl font-bold text-indigo-600">{data.overview.categories}</p>
              </div>
              <Activity className="text-indigo-500" size={32} />
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Licenses</p>
                <p className="text-3xl font-bold text-pink-600">{data.overview.licenses}</p>
              </div>
              <Users className="text-pink-500" size={32} />
            </div>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Category Distribution */}
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">📦 Tools by Category</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={data.category_distribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({name, percentage}) => `${name} (${percentage}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {data.category_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Pricing Distribution */}
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">💰 Pricing Models</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.pricing_distribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Tools */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 mb-12">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">🏆 Top Tools by Stars</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Rank</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Tool</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Category</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Stars</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Forks</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">License</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Pricing</th>
                </tr>
              </thead>
              <tbody>
                {data.top_tools.map((tool, index) => (
                  <tr key={tool.name} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <span className="font-bold text-blue-600">#{index + 1}</span>
                    </td>
                    <td className="py-3 px-4 font-semibold text-gray-900">{tool.name}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                        {tool.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-yellow-600 font-semibold">
                      {tool.stars.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-green-600 font-semibold">
                      {tool.forks.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-gray-600">{tool.license}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded-full text-sm ${
                        tool.pricing === 'free' ? 'bg-green-100 text-green-800' :
                        tool.pricing === 'freemium' ? 'bg-blue-100 text-blue-800' :
                        'bg-purple-100 text-purple-800'
                      }`}>
                        {tool.pricing}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Insights */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">💡 Key Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {data.insights.map((insight, index) => (
              <div key={index} className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-6">
                <p className="text-blue-900 font-medium">{insight}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
