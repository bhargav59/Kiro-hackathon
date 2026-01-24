import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
    Plus, Trash2, Edit, RefreshCw, Github, Sparkles,
    TrendingUp, FileText, Settings, AlertCircle, CheckCircle,
    Loader2, ExternalLink, Star, GitFork, BookOpen
} from 'lucide-react';
import { API_BASE } from '../config';

// Types
interface Blog {
    id: number;
    title: string;
    content: string;
    author: string;
    created_at: string;
    updated_at?: string;
    word_count?: number;
}

interface TrendingRepo {
    name: string;
    url: string;
    description: string;
    stars: number;
    forks: number;
    language: string;
    topics: string[];
    trending_rank: number;
}

interface AIStatus {
    configured: boolean;
    model: string;
    features: string[];
}

const AdminDashboard: React.FC = () => {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<'blogs' | 'generate' | 'settings'>('blogs');
    const [blogs, setBlogs] = useState<Blog[]>([]);
    const [trendingRepos, setTrendingRepos] = useState<TrendingRepo[]>([]);
    const [aiStatus, setAIStatus] = useState<AIStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Custom topic form
    const [customTopic, setCustomTopic] = useState('');
    const [articleStyle, setArticleStyle] = useState('tutorial');
    const [articleLength, setArticleLength] = useState('medium');

    // Edit modal
    const [editingBlog, setEditingBlog] = useState<Blog | null>(null);
    const [editTitle, setEditTitle] = useState('');
    const [editContent, setEditContent] = useState('');

    const token = localStorage.getItem('token');

    useEffect(() => {
        if (!token) {
            navigate('/login');
            return;
        }
        fetchBlogs();
        fetchAIStatus();
    }, [token, navigate]);

    // Auth headers
    const getHeaders = () => ({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    });

    // Fetch blogs
    const fetchBlogs = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/admin/blogs`, {
                headers: getHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setBlogs(data.blogs || []);
            } else if (response.status === 401) {
                // Fallback to public endpoint for non-authenticated view
                const publicResponse = await fetch(`${API_BASE}/api/blogs`);
                const publicData = await publicResponse.json();
                setBlogs(publicData);
            }
        } catch (err) {
            console.error('Error fetching blogs:', err);
        } finally {
            setLoading(false);
        }
    };

    // Fetch AI status
    const fetchAIStatus = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/admin/ai-status`);
            const data = await response.json();
            setAIStatus(data);
        } catch (err) {
            console.error('Error fetching AI status:', err);
        }
    };

    // Fetch trending repos
    const fetchTrendingRepos = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/api/admin/github/trending?limit=10`);
            const data = await response.json();
            setTrendingRepos(data.repos || []);
        } catch (err) {
            setError('Failed to fetch trending repositories');
        } finally {
            setLoading(false);
        }
    };

    // Generate from GitHub repo
    const generateFromGitHub = async (repoUrl: string) => {
        setGenerating(true);
        setError('');
        setSuccess('');

        try {
            const response = await fetch(`${API_BASE}/api/admin/blogs/generate-from-github`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({
                    repo_url: repoUrl,
                    style: articleStyle,
                    length: articleLength
                })
            });

            if (response.ok) {
                const data = await response.json();
                setSuccess(`Blog "${data.title}" generated successfully!`);
                fetchBlogs();
                setActiveTab('blogs');
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to generate blog');
            }
        } catch (err) {
            setError('Network error. Please try again.');
        } finally {
            setGenerating(false);
        }
    };

    // Generate from custom topic
    const generateFromTopic = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!customTopic.trim()) return;

        setGenerating(true);
        setError('');
        setSuccess('');

        try {
            const response = await fetch(`${API_BASE}/api/admin/blogs/generate-from-topic`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({
                    topic: customTopic,
                    style: articleStyle,
                    length: articleLength
                })
            });

            if (response.ok) {
                const data = await response.json();
                setSuccess(`Blog "${data.title}" generated successfully!`);
                setCustomTopic('');
                fetchBlogs();
                setActiveTab('blogs');
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to generate blog');
            }
        } catch (err) {
            setError('Network error. Please try again.');
        } finally {
            setGenerating(false);
        }
    };

    // Delete blog
    const deleteBlog = async (blogId: number) => {
        if (!confirm('Are you sure you want to delete this blog?')) return;

        try {
            const response = await fetch(`${API_BASE}/api/admin/blogs/${blogId}`, {
                method: 'DELETE',
                headers: getHeaders()
            });

            if (response.ok) {
                setSuccess('Blog deleted successfully');
                fetchBlogs();
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to delete blog');
            }
        } catch (err) {
            setError('Network error. Please try again.');
        }
    };

    // Update blog
    const updateBlog = async () => {
        if (!editingBlog) return;

        try {
            const response = await fetch(`${API_BASE}/api/admin/blogs/${editingBlog.id}`, {
                method: 'PUT',
                headers: getHeaders(),
                body: JSON.stringify({
                    title: editTitle,
                    content: editContent
                })
            });

            if (response.ok) {
                setSuccess('Blog updated successfully');
                setEditingBlog(null);
                fetchBlogs();
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to update blog');
            }
        } catch (err) {
            setError('Network error. Please try again.');
        }
    };

    // Open edit modal
    const openEditModal = (blog: Blog) => {
        setEditingBlog(blog);
        setEditTitle(blog.title);
        setEditContent(blog.content);
    };

    // Clear messages
    useEffect(() => {
        if (success || error) {
            const timer = setTimeout(() => {
                setSuccess('');
                setError('');
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [success, error]);

    // Load trending repos when switching to generate tab
    useEffect(() => {
        if (activeTab === 'generate' && trendingRepos.length === 0) {
            fetchTrendingRepos();
        }
    }, [activeTab]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
            {/* Header */}
            <header className="bg-black/30 backdrop-blur-xl border-b border-white/10">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                                <Settings className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold text-white">Admin Dashboard</h1>
                                <p className="text-sm text-gray-400">Manage blogs & AI content generation</p>
                            </div>
                        </div>

                        {/* AI Status Badge */}
                        {aiStatus && (
                            <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${aiStatus.configured
                                    ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                                    : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                                }`}>
                                <Sparkles className="w-4 h-4" />
                                <span className="text-sm font-medium">
                                    AI: {aiStatus.configured ? 'Active' : 'Not Configured'}
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            </header>

            {/* Tabs */}
            <div className="max-w-7xl mx-auto px-6 py-4">
                <div className="flex gap-2 bg-black/20 p-1 rounded-xl w-fit">
                    <button
                        onClick={() => setActiveTab('blogs')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${activeTab === 'blogs'
                                ? 'bg-purple-600 text-white'
                                : 'text-gray-400 hover:text-white hover:bg-white/10'
                            }`}
                    >
                        <FileText className="w-4 h-4" />
                        Manage Blogs
                    </button>
                    <button
                        onClick={() => setActiveTab('generate')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${activeTab === 'generate'
                                ? 'bg-purple-600 text-white'
                                : 'text-gray-400 hover:text-white hover:bg-white/10'
                            }`}
                    >
                        <Sparkles className="w-4 h-4" />
                        AI Generate
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div className="max-w-7xl mx-auto px-6">
                {error && (
                    <div className="mb-4 bg-red-500/20 border border-red-500/30 text-red-400 px-4 py-3 rounded-xl flex items-center gap-2">
                        <AlertCircle className="w-5 h-5" />
                        {error}
                    </div>
                )}
                {success && (
                    <div className="mb-4 bg-green-500/20 border border-green-500/30 text-green-400 px-4 py-3 rounded-xl flex items-center gap-2">
                        <CheckCircle className="w-5 h-5" />
                        {success}
                    </div>
                )}
            </div>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-6 pb-12">
                {/* Manage Blogs Tab */}
                {activeTab === 'blogs' && (
                    <div className="bg-black/20 backdrop-blur-xl rounded-2xl border border-white/10 overflow-hidden">
                        <div className="p-6 border-b border-white/10 flex justify-between items-center">
                            <div>
                                <h2 className="text-xl font-bold text-white">Published Articles</h2>
                                <p className="text-gray-400 text-sm">{blogs.length} articles total</p>
                            </div>
                            <button
                                onClick={fetchBlogs}
                                className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
                            >
                                <RefreshCw className="w-4 h-4" />
                                Refresh
                            </button>
                        </div>

                        {loading ? (
                            <div className="p-12 text-center">
                                <Loader2 className="w-8 h-8 text-purple-500 animate-spin mx-auto mb-4" />
                                <p className="text-gray-400">Loading blogs...</p>
                            </div>
                        ) : blogs.length === 0 ? (
                            <div className="p-12 text-center">
                                <FileText className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                                <p className="text-gray-400 mb-4">No blogs yet. Generate your first article!</p>
                                <button
                                    onClick={() => setActiveTab('generate')}
                                    className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium transition-colors"
                                >
                                    Generate with AI
                                </button>
                            </div>
                        ) : (
                            <div className="divide-y divide-white/10">
                                {blogs.map((blog) => (
                                    <div key={blog.id} className="p-6 hover:bg-white/5 transition-colors">
                                        <div className="flex justify-between items-start gap-4">
                                            <div className="flex-1">
                                                <Link
                                                    to={`/blog/${blog.id}`}
                                                    className="text-lg font-semibold text-white hover:text-purple-400 transition-colors"
                                                >
                                                    {blog.title}
                                                </Link>
                                                <p className="text-gray-400 text-sm mt-1 line-clamp-2">
                                                    {blog.content?.substring(0, 150).replace(/[#*`]/g, '')}...
                                                </p>
                                                <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                                                    <span>By {blog.author}</span>
                                                    <span>•</span>
                                                    <span>{new Date(blog.created_at).toLocaleDateString()}</span>
                                                    {blog.word_count && (
                                                        <>
                                                            <span>•</span>
                                                            <span>{blog.word_count} words</span>
                                                        </>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <button
                                                    onClick={() => openEditModal(blog)}
                                                    className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                                                    title="Edit"
                                                >
                                                    <Edit className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={() => deleteBlog(blog.id)}
                                                    className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                                                    title="Delete"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* AI Generate Tab */}
                {activeTab === 'generate' && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Generate from Custom Topic */}
                        <div className="bg-black/20 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                                    <Sparkles className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-white">Generate from Topic</h3>
                                    <p className="text-gray-400 text-sm">Create article from any DevOps topic</p>
                                </div>
                            </div>

                            <form onSubmit={generateFromTopic} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Topic</label>
                                    <input
                                        type="text"
                                        value={customTopic}
                                        onChange={(e) => setCustomTopic(e.target.value)}
                                        placeholder="e.g., Kubernetes Best Practices for Production"
                                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">Style</label>
                                        <select
                                            value={articleStyle}
                                            onChange={(e) => setArticleStyle(e.target.value)}
                                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                                        >
                                            <option value="tutorial">Tutorial</option>
                                            <option value="comparison">Comparison</option>
                                            <option value="news">News</option>
                                            <option value="deep-dive">Deep Dive</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">Length</label>
                                        <select
                                            value={articleLength}
                                            onChange={(e) => setArticleLength(e.target.value)}
                                            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                                        >
                                            <option value="short">Short (500-800 words)</option>
                                            <option value="medium">Medium (1000-1500 words)</option>
                                            <option value="long">Long (2000+ words)</option>
                                        </select>
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    disabled={generating || !customTopic.trim()}
                                    className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {generating ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                            Generating...
                                        </>
                                    ) : (
                                        <>
                                            <Sparkles className="w-5 h-5" />
                                            Generate Article
                                        </>
                                    )}
                                </button>
                            </form>
                        </div>

                        {/* Trending GitHub Repos */}
                        <div className="bg-black/20 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-gradient-to-br from-gray-700 to-gray-900 rounded-xl flex items-center justify-center">
                                        <Github className="w-5 h-5 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-white">Trending Repositories</h3>
                                        <p className="text-gray-400 text-sm">Generate from popular GitHub repos</p>
                                    </div>
                                </div>
                                <button
                                    onClick={fetchTrendingRepos}
                                    disabled={loading}
                                    className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                                >
                                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                                </button>
                            </div>

                            <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                                {loading ? (
                                    <div className="text-center py-8">
                                        <Loader2 className="w-6 h-6 text-purple-500 animate-spin mx-auto mb-2" />
                                        <p className="text-gray-400 text-sm">Loading trending repos...</p>
                                    </div>
                                ) : trendingRepos.length === 0 ? (
                                    <div className="text-center py-8">
                                        <TrendingUp className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                                        <p className="text-gray-400 text-sm">Click refresh to load trending repos</p>
                                    </div>
                                ) : (
                                    trendingRepos.map((repo, index) => (
                                        <div
                                            key={repo.url}
                                            className="bg-white/5 hover:bg-white/10 rounded-xl p-4 transition-colors group"
                                        >
                                            <div className="flex justify-between items-start gap-3">
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="text-purple-400 text-xs font-medium">#{index + 1}</span>
                                                        <a
                                                            href={repo.url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="font-medium text-white hover:text-purple-400 transition-colors truncate flex items-center gap-1"
                                                        >
                                                            {repo.name}
                                                            <ExternalLink className="w-3 h-3 opacity-50" />
                                                        </a>
                                                    </div>
                                                    <p className="text-gray-400 text-sm line-clamp-2 mb-2">
                                                        {repo.description || 'No description'}
                                                    </p>
                                                    <div className="flex items-center gap-3 text-xs text-gray-500">
                                                        <span className="flex items-center gap-1">
                                                            <Star className="w-3 h-3" />
                                                            {(repo.stars / 1000).toFixed(1)}k
                                                        </span>
                                                        <span className="flex items-center gap-1">
                                                            <GitFork className="w-3 h-3" />
                                                            {(repo.forks / 1000).toFixed(1)}k
                                                        </span>
                                                        {repo.language && (
                                                            <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded">
                                                                {repo.language}
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={() => generateFromGitHub(repo.url)}
                                                    disabled={generating}
                                                    className="shrink-0 px-3 py-2 bg-purple-600/20 hover:bg-purple-600 text-purple-400 hover:text-white rounded-lg text-sm font-medium transition-all opacity-0 group-hover:opacity-100"
                                                >
                                                    {generating ? (
                                                        <Loader2 className="w-4 h-4 animate-spin" />
                                                    ) : (
                                                        <BookOpen className="w-4 h-4" />
                                                    )}
                                                </button>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </main>

            {/* Edit Modal */}
            {editingBlog && (
                <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
                    <div className="bg-slate-900 rounded-2xl border border-white/10 w-full max-w-3xl max-h-[90vh] overflow-hidden">
                        <div className="p-6 border-b border-white/10 flex justify-between items-center">
                            <h3 className="text-lg font-bold text-white">Edit Blog</h3>
                            <button
                                onClick={() => setEditingBlog(null)}
                                className="text-gray-400 hover:text-white transition-colors"
                            >
                                ✕
                            </button>
                        </div>
                        <div className="p-6 space-y-4 overflow-y-auto max-h-[60vh]">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">Title</label>
                                <input
                                    type="text"
                                    value={editTitle}
                                    onChange={(e) => setEditTitle(e.target.value)}
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">Content</label>
                                <textarea
                                    value={editContent}
                                    onChange={(e) => setEditContent(e.target.value)}
                                    rows={12}
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
                                />
                            </div>
                        </div>
                        <div className="p-6 border-t border-white/10 flex justify-end gap-3">
                            <button
                                onClick={() => setEditingBlog(null)}
                                className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={updateBlog}
                                className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                            >
                                Save Changes
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminDashboard;
