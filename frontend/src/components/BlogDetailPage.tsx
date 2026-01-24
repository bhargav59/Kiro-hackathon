import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Calendar, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { generateThumbnail, getTechIcon } from '../utils/thumbnails';

interface Blog {
  id: number;
  title: string;
  content: string;
  author: string;
  created_at: string;
  updated_at?: string;
}

const BlogDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [blog, setBlog] = useState<Blog | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchBlog = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/blogs');
        const blogs = await response.json();
        const foundBlog = blogs.find((b: Blog) => b.id === parseInt(id || '0'));

        if (foundBlog) {
          setBlog(foundBlog);
        } else {
          setError('Blog not found');
        }
      } catch (err) {
        setError('Failed to load blog');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchBlog();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading blog...</p>
        </div>
      </div>
    );
  }

  if (error || !blog) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Blog Not Found</h1>
          <p className="text-gray-600 mb-6">{error || 'The requested blog could not be found.'}</p>
          <Link
            to="/admin"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 inline-flex items-center"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back to Blogs
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <style>{`
        pre {
          background: #1a1a1a !important;
          color: #e6e6e6 !important;
        }
        code {
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }
      `}</style>
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <Link
            to="/admin"
            className="text-blue-600 hover:text-blue-800 inline-flex items-center mb-4"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back to All Blogs
          </Link>
        </div>
      </div>

      {/* Blog Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <article className="bg-white rounded-lg shadow-lg p-8">
          {/* Blog Header with Thumbnail */}
          <div className="relative mb-8">
            <div className="h-64 rounded-xl overflow-hidden mb-6">
              <img
                src={generateThumbnail(blog.title)}
                alt={blog.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
              <div className="absolute bottom-6 left-6 text-white">
                <div className="flex items-center mb-2">
                  <span className="text-4xl mr-3">{getTechIcon(blog.title)}</span>
                  <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium">
                    Technical Guide
                  </span>
                </div>
              </div>
            </div>

            <header className="pb-6 border-b border-gray-200">
              <h1 className="text-4xl font-bold text-gray-900 mb-4 leading-tight">
                {blog.title}
              </h1>

              <div className="flex items-center text-gray-600 space-x-6">
                <div className="flex items-center">
                  <User size={18} className="mr-2" />
                  <span className="font-medium">{blog.author}</span>
                </div>
                <div className="flex items-center">
                  <Calendar size={18} className="mr-2" />
                  <span>{new Date(blog.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}</span>
                </div>
              </div>
            </header>
          </div>

          {/* Blog Content */}
          <div className="prose prose-lg max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({ children }) => <h1 className="text-3xl font-bold text-gray-900 mt-8 mb-4 border-b-2 border-blue-200 pb-2">{children}</h1>,
                h2: ({ children }) => <h2 className="text-2xl font-semibold text-blue-700 mt-6 mb-3">{children}</h2>,
                h3: ({ children }) => <h3 className="text-xl font-semibold text-gray-800 mt-5 mb-2">{children}</h3>,
                p: ({ children }) => <p className="text-gray-700 leading-relaxed mb-4">{children}</p>,
                code: (props: any) =>
                  props.inline ?
                    <code className="bg-gray-100 text-red-600 px-1 py-0.5 rounded text-sm font-mono">{props.children}</code> :
                    <code className="block bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm font-mono whitespace-pre">{props.children}</code>,
                pre: ({ children }) => <div className="bg-gray-900 rounded-lg p-4 mb-4 overflow-x-auto">{children}</div>,
                ul: ({ children }) => <ul className="list-disc list-inside mb-4 space-y-1 text-gray-700">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-4 space-y-1 text-gray-700">{children}</ol>,
                li: ({ children }) => <li className="mb-1">{children}</li>,
                strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                table: ({ children }) => <table className="min-w-full border-collapse border border-gray-300 mb-6 bg-white rounded-lg overflow-hidden shadow-sm">{children}</table>,
                thead: ({ children }) => <thead className="bg-gray-50">{children}</thead>,
                tbody: ({ children }) => <tbody>{children}</tbody>,
                tr: ({ children }) => <tr className="border-b border-gray-200 hover:bg-gray-50">{children}</tr>,
                th: ({ children }) => <th className="border border-gray-300 px-4 py-3 text-left font-semibold text-gray-900 bg-blue-50">{children}</th>,
                td: ({ children }) => <td className="border border-gray-300 px-4 py-3 text-gray-700">{children}</td>,
              }}
            >
              {blog.content}
            </ReactMarkdown>
          </div>

          {/* Footer */}
          <footer className="mt-12 pt-6 border-t border-gray-200">
            <div className="flex justify-center">
              <Link
                to="/admin"
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 inline-flex items-center"
              >
                <ArrowLeft size={18} className="mr-2" />
                Back to All Blogs
              </Link>
            </div>
          </footer>
        </article>
      </div>
    </div>
  );
};

export default BlogDetailPage;
