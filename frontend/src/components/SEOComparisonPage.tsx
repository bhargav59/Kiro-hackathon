import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Eye, Calendar } from 'lucide-react';
import { API_BASE } from '../config';
import { trackEvent } from '../analytics';

interface ComparisonData {
  id: number;
  slug: string;
  title: string;
  content: string;
  meta_description: string;
  views: number;
  tool_a: { id: number; name: string; slug: string } | null;
  tool_b: { id: number; name: string; slug: string } | null;
  generated_at: string | null;
}

const SEOComparisonPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [data, setData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!slug) return;
    fetchComparison();
  }, [slug]);

  const fetchComparison = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/comparisons/${slug}`);
      if (res.ok) {
        const result = await res.json();
        setData(result);
        trackEvent('comparison_page_viewed', { slug, tool_a: result.tool_a?.name, tool_b: result.tool_b?.name });

        // Update document title for SEO
        document.title = result.title + ' | CloudEngineered';
        const metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc) metaDesc.setAttribute('content', result.meta_description);
      } else {
        setError('Comparison not found');
      }
    } catch {
      setError('Failed to load comparison');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-4xl mx-auto p-6 text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Comparison Not Found</h1>
        <p className="text-gray-500 mb-4">{error}</p>
        <Link to="/compare" className="text-blue-600 hover:underline">Browse all comparisons</Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Link to="/compare" className="inline-flex items-center gap-1 text-blue-600 hover:underline mb-4">
        <ArrowLeft size={16} /> All Comparisons
      </Link>

      <h1 className="text-3xl font-bold text-gray-900 mb-2">{data.title}</h1>

      <div className="flex items-center gap-4 text-sm text-gray-500 mb-6">
        <span className="flex items-center gap-1"><Eye size={14} /> {data.views} views</span>
        {data.generated_at && (
          <span className="flex items-center gap-1">
            <Calendar size={14} /> {new Date(data.generated_at).toLocaleDateString()}
          </span>
        )}
      </div>

      {/* Tool links */}
      <div className="flex gap-3 mb-6">
        {data.tool_a && (
          <Link
            to={`/tools/${data.tool_a.slug}`}
            className="px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 font-medium text-sm"
          >
            {data.tool_a.name} Details
          </Link>
        )}
        {data.tool_b && (
          <Link
            to={`/tools/${data.tool_b.slug}`}
            className="px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 font-medium text-sm"
          >
            {data.tool_b.name} Details
          </Link>
        )}
      </div>

      {/* Render markdown content as HTML */}
      <div className="prose prose-lg max-w-none">
        {data.content.split('\n').map((line, i) => {
          if (line.startsWith('## ')) return <h2 key={i} className="text-2xl font-bold mt-8 mb-4">{line.slice(3)}</h2>;
          if (line.startsWith('### ')) return <h3 key={i} className="text-xl font-semibold mt-6 mb-3">{line.slice(4)}</h3>;
          if (line.startsWith('| ')) {
            const cells = line.split('|').filter(Boolean).map(c => c.trim());
            const isHeader = cells.every(c => c.startsWith('**') || c.startsWith('---'));
            if (cells.every(c => c.match(/^-+$/))) return null; // Skip separator rows
            return (
              <div key={i} className={`grid grid-cols-${cells.length} gap-2 py-2 px-3 ${isHeader ? 'font-semibold bg-gray-50' : 'border-b border-gray-100'}`}>
                {cells.map((cell, j) => (
                  <span key={j} className="text-sm" dangerouslySetInnerHTML={{ __html: cell.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
                ))}
              </div>
            );
          }
          if (line.startsWith('- ')) return <li key={i} className="ml-4 text-gray-700" dangerouslySetInnerHTML={{ __html: line.slice(2).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />;
          if (line.trim() === '') return <div key={i} className="h-2" />;
          return <p key={i} className="text-gray-700 mb-2" dangerouslySetInnerHTML={{ __html: line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />;
        })}
      </div>
    </div>
  );
};

export default SEOComparisonPage;
