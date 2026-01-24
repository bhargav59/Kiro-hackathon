import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { generateThumbnail, getTechIcon } from '../utils/thumbnails';

interface Blog {
  id: number;
  title: string;
  content: string;
  author: string;
  created_at: string;
  updated_at?: string;
}

const AdminPage: React.FC = () => {
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBlogs();
  }, []);

  const fetchBlogs = async () => {
    console.log('Fetching blogs...');
    try {
      const response = await fetch('http://localhost:8000/api/blogs');
      const data = await response.json();
      console.log('Blogs fetched:', data.length);
      setBlogs(data);
    } catch (error) {
      console.error('Error fetching blogs:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading blogs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
      <style>{`
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        .line-clamp-3 {
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Technical Blog Collection</h1>
          <p className="text-gray-600">Comprehensive guides for modern development and infrastructure</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-semibold text-gray-800">Published Articles</h2>
            <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
              {blogs.length} Articles
            </span>
          </div>
          
          {blogs.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">No blogs found</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {blogs.map((blog) => (
                <div key={blog.id} className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group">
                  {/* Thumbnail */}
                  <div className="relative h-48 overflow-hidden">
                    <img 
                      src={generateThumbnail(blog.title)} 
                      alt={blog.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-4 left-4">
                      <span className="text-3xl">{getTechIcon(blog.title)}</span>
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
                      <span className="text-white text-sm font-medium">Technical Guide</span>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-6">
                    <Link to={`/blog/${blog.id}`} className="block group-hover:text-blue-600 transition-colors">
                      <h3 className="text-lg font-bold text-gray-900 mb-3 line-clamp-2 leading-tight">
                        {blog.title}
                      </h3>
                    </Link>
                    
                    <div className="flex items-center text-sm text-gray-500 mb-3">
                      <span className="font-medium text-blue-600">{blog.author}</span>
                      <span className="mx-2">•</span>
                      <span>{new Date(blog.created_at).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric',
                        year: 'numeric'
                      })}</span>
                    </div>

                    <p className="text-gray-600 text-sm leading-relaxed mb-4 line-clamp-3">
                      {blog.content.substring(0, 150).replace(/[#*`]/g, '')}...
                    </p>

                    <Link 
                      to={`/blog/${blog.id}`}
                      className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium text-sm group-hover:translate-x-1 transition-transform"
                    >
                      Read Article
                      <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="mt-8 text-center">
          <p className="text-gray-500">
            Total articles: {blogs.length}
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;
