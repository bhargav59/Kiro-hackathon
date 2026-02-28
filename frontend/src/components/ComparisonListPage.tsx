import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { ArrowRight, Eye, Calendar } from 'lucide-react';

import { API_BASE } from '../config';

interface ComparisonItem {
  id: number;
  slug: string;
  title: string;
  meta_description: string;
  views: number;
  generated_at: string;
}

const fetchComparisons = async (): Promise<ComparisonItem[]> => {
  const response = await fetch(`${API_BASE}/api/comparisons`);
  if (!response.ok) throw new Error('Failed to fetch comparisons');
  return response.json();
};

const ComparisonListPage: React.FC = () => {
  const { data: comparisons = [], isLoading, isError, error } = useQuery({
    queryKey: ['comparisons'],
    queryFn: fetchComparisons,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="text-center text-red-600">
          <h2 className="text-xl font-semibold">Error loading comparisons</h2>
          <p className="mt-2">{error instanceof Error ? error.message : 'Unknown error'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">
            Tool Comparisons
          </h1>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
            In-depth comparisons of popular DevOps and cloud engineering tools
            to help you make informed decisions.
          </p>
        </div>

        {comparisons.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">No comparisons yet</h3>
            <p className="text-gray-600 mb-6">Check back soon for detailed tool comparisons.</p>
            <Link
              to="/compare"
              className="inline-flex items-center bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
            >
              Generate a Comparison <ArrowRight size={18} className="ml-2" />
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {comparisons.map((comp) => (
              <Link
                key={comp.id}
                to={`/compare/${comp.slug}`}
                className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 block"
              >
                <h3 className="text-xl font-bold text-gray-900 mb-3">{comp.title}</h3>
                <p className="text-gray-600 leading-relaxed mb-6 line-clamp-3">
                  {comp.meta_description}
                </p>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center space-x-4">
                    <span className="flex items-center">
                      <Eye size={14} className="mr-1" />
                      {comp.views.toLocaleString()} views
                    </span>
                    {comp.generated_at && (
                      <span className="flex items-center">
                        <Calendar size={14} className="mr-1" />
                        {new Date(comp.generated_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                  <ArrowRight size={16} className="text-blue-600" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ComparisonListPage;
