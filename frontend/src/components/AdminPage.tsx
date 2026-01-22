import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Save, X, LogIn } from 'lucide-react';

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
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingBlog, setEditingBlog] = useState<Blog | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [signupForm, setSignupForm] = useState({ username: '', email: '', password: '' });
  const [showSignup, setShowSignup] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [showResetPassword, setShowResetPassword] = useState(false);
  const [forgotPasswordEmail, setForgotPasswordEmail] = useState('');
  const [resetPasswordData, setResetPasswordData] = useState({ token: '', newPassword: '' });
  const [resetToken, setResetToken] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    excerpt: '',
    content: '',
    author: 'Admin',
    category: 'Technology',
    tags: '',
    featured_image: '',
    status: 'published'
  });

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
      fetchBlogs();
    }
  }, []);

  const fetchBlogs = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/blogs');
      const data = await response.json();
      setBlogs(data);
    } catch (error) {
      console.error('Error fetching blogs:', error);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm),
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        setIsAuthenticated(true);
        fetchBlogs();
      } else {
        alert('Invalid credentials');
      }
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: forgotPasswordEmail }),
      });
      
      if (response.ok) {
        const data = await response.json();
        alert('Password reset instructions sent to your email!');
        // For demo purposes, show the reset token
        if (data.reset_token) {
          setResetToken(data.reset_token);
          setResetPasswordData({ ...resetPasswordData, token: data.reset_token });
          setShowResetPassword(true);
        }
        setShowForgotPassword(false);
      }
    } catch (error) {
      console.error('Forgot password error:', error);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: resetPasswordData.token,
          new_password: resetPasswordData.newPassword,
        }),
      });
      
      if (response.ok) {
        alert('Password reset successfully! You can now login with your new password.');
        setShowResetPassword(false);
        setResetPasswordData({ token: '', newPassword: '' });
        setResetToken('');
      } else {
        const error = await response.json();
        alert(error.detail || 'Password reset failed');
      }
    } catch (error) {
      console.error('Reset password error:', error);
    }
  };
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(signupForm),
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        setIsAuthenticated(true);
        fetchBlogs();
      } else {
        const error = await response.json();
        alert(error.detail || 'Signup failed');
      }
    } catch (error) {
      console.error('Signup error:', error);
    }
  };

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/blogs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        setFormData({ 
          title: '', excerpt: '', content: '', author: 'Admin', 
          category: 'Technology', tags: '', featured_image: '', status: 'published' 
        });
        setShowCreateForm(false);
        fetchBlogs();
      }
    } catch (error) {
      console.error('Error creating blog:', error);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingBlog) return;
    
    try {
      const response = await fetch(`http://localhost:8000/api/blogs/${editingBlog.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify({
          title: editingBlog.title,
          content: editingBlog.content,
        }),
      });
      
      if (response.ok) {
        setEditingBlog(null);
        fetchBlogs();
      }
    } catch (error) {
      console.error('Error updating blog:', error);
    }
  };

  const deleteBlog = async (id: number) => {
    if (confirm('Are you sure you want to delete this blog?')) {
      try {
        await fetch(`http://localhost:8000/api/blogs/${id}`, {
          method: 'DELETE',
          headers: getAuthHeaders(),
        });
        fetchBlogs();
      } catch (error) {
        console.error('Error deleting blog:', error);
      }
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setBlogs([]);
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
          <h1 className="text-2xl font-bold text-center mb-6">Admin Access</h1>
          
          {showResetPassword ? (
            <form onSubmit={handleResetPassword} className="space-y-4">
              <h2 className="text-lg font-semibold">Reset Password</h2>
              <p className="text-sm text-gray-600 mb-4">
                Reset token: <code className="bg-gray-100 p-1 rounded text-xs">{resetToken}</code>
              </p>
              <input
                type="password"
                placeholder="New Password"
                value={resetPasswordData.newPassword}
                onChange={(e) => setResetPasswordData({ ...resetPasswordData, newPassword: e.target.value })}
                className="w-full p-3 border rounded-lg"
                required
              />
              <button
                type="submit"
                className="w-full bg-green-600 text-white p-3 rounded-lg hover:bg-green-700"
              >
                Reset Password
              </button>
              <button
                type="button"
                onClick={() => setShowResetPassword(false)}
                className="w-full text-blue-600 hover:underline"
              >
                Back to Login
              </button>
            </form>
          ) : showForgotPassword ? (
            <form onSubmit={handleForgotPassword} className="space-y-4">
              <h2 className="text-lg font-semibold">Forgot Password</h2>
              <input
                type="email"
                placeholder="Enter your email"
                value={forgotPasswordEmail}
                onChange={(e) => setForgotPasswordEmail(e.target.value)}
                className="w-full p-3 border rounded-lg"
                required
              />
              <button
                type="submit"
                className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700"
              >
                Send Reset Link
              </button>
              <button
                type="button"
                onClick={() => setShowForgotPassword(false)}
                className="w-full text-blue-600 hover:underline"
              >
                Back to Login
              </button>
            </form>
          ) : !showSignup ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <h2 className="text-lg font-semibold">Login</h2>
              <input
                type="email"
                placeholder="Email"
                value={loginForm.email}
                onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                className="w-full p-3 border rounded-lg"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                className="w-full p-3 border rounded-lg"
                required
              />
              <button
                type="submit"
                className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700"
              >
                Login
              </button>
              <p className="text-center">
                Don't have an account?{' '}
                <button
                  type="button"
                  onClick={() => setShowSignup(true)}
                  className="text-blue-600 hover:underline"
                >
                  Sign up
                </button>
              </p>
              <p className="text-center">
                <button
                  type="button"
                  onClick={() => setShowForgotPassword(true)}
                  className="text-blue-600 hover:underline text-sm"
                >
                  Forgot Password?
                </button>
              </p>
            </form>
          ) : (
            <form onSubmit={handleSignup} className="space-y-4">
              <h2 className="text-lg font-semibold">Sign Up</h2>
              <input
                type="text"
                placeholder="Username"
                value={signupForm.username}
                onChange={(e) => setSignupForm({ ...signupForm, username: e.target.value })}
                className="w-full p-3 border rounded-lg"
                required
              />
              <input
                type="email"
                placeholder="Email"
                value={signupForm.email}
                onChange={(e) => setSignupForm({ ...signupForm, email: e.target.value })}
                className="w-full p-3 border rounded-lg"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={signupForm.password}
                onChange={(e) => setSignupForm({ ...signupForm, password: e.target.value })}
                className="w-full p-3 border rounded-lg"
                required
              />
              <button
                type="submit"
                className="w-full bg-green-600 text-white p-3 rounded-lg hover:bg-green-700"
              >
                Sign Up
              </button>
              <p className="text-center">
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => setShowSignup(false)}
                  className="text-blue-600 hover:underline"
                >
                  Login
                </button>
              </p>
            </form>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <div className="flex gap-3">
              <button
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
              >
                <Plus size={20} />
                Create Blog
              </button>
              <button
                onClick={logout}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>

          {showCreateForm && (
            <div className="bg-gray-50 p-6 rounded-lg mb-6">
              <h2 className="text-xl font-semibold mb-4">Create New Blog</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Blog Title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full p-3 border rounded-lg"
                    required
                  />
                  <input
                    type="text"
                    placeholder="Author"
                    value={formData.author}
                    onChange={(e) => setFormData({ ...formData, author: e.target.value })}
                    className="w-full p-3 border rounded-lg"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full p-3 border rounded-lg"
                  >
                    <option value="Technology">Technology</option>
                    <option value="Cloud Computing">Cloud Computing</option>
                    <option value="DevOps">DevOps</option>
                    <option value="Security">Security</option>
                    <option value="Architecture">Architecture</option>
                    <option value="Database">Database</option>
                    <option value="API Development">API Development</option>
                    <option value="Machine Learning">Machine Learning</option>
                    <option value="Infrastructure">Infrastructure</option>
                    <option value="SRE">SRE</option>
                  </select>
                  <input
                    type="text"
                    placeholder="Tags (comma separated)"
                    value={formData.tags}
                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                    className="w-full p-3 border rounded-lg"
                  />
                </div>
                <textarea
                  placeholder="Blog Excerpt (brief summary)"
                  value={formData.excerpt}
                  onChange={(e) => setFormData({ ...formData, excerpt: e.target.value })}
                  rows={3}
                  className="w-full p-3 border rounded-lg"
                  required
                />
                <textarea
                  placeholder="Blog Content"
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  rows={12}
                  className="w-full p-3 border rounded-lg"
                  required
                />
                <div className="flex gap-3">
                  <button type="submit" className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700">
                    <Save size={20} className="inline mr-2" />
                    Save Blog
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Blog Posts ({blogs.length})</h2>
            {blogs.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No blogs created yet</p>
            ) : (
              <div className="grid gap-4">
                {blogs.map((blog) => (
                  <div key={blog.id} className="border border-gray-200 rounded-lg p-4">
                    {editingBlog?.id === blog.id ? (
                      <form onSubmit={handleUpdate} className="space-y-3">
                        <input
                          type="text"
                          value={editingBlog.title}
                          onChange={(e) => setEditingBlog({ ...editingBlog, title: e.target.value })}
                          className="w-full p-2 border rounded"
                        />
                        <textarea
                          value={editingBlog.content}
                          onChange={(e) => setEditingBlog({ ...editingBlog, content: e.target.value })}
                          rows={6}
                          className="w-full p-2 border rounded"
                        />
                        <div className="flex gap-2">
                          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                            <Save size={16} className="inline mr-1" />
                            Save
                          </button>
                          <button
                            type="button"
                            onClick={() => setEditingBlog(null)}
                            className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                          >
                            <X size={16} className="inline mr-1" />
                            Cancel
                          </button>
                        </div>
                      </form>
                    ) : (
                      <>
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">{blog.title}</h3>
                            <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">{blog.category}</span>
                              <span>👁 {blog.view_count || 0} views</span>
                              <span>📖 {blog.reading_time || 5} min read</span>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={() => setEditingBlog(blog)}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <Edit size={18} />
                            </button>
                            <button
                              onClick={() => deleteBlog(blog.id)}
                              className="text-red-600 hover:text-red-800"
                            >
                              <Trash2 size={18} />
                            </button>
                          </div>
                        </div>
                        <p className="text-gray-600 mb-2">By {blog.author}</p>
                        <p className="text-gray-700 mb-2 font-medium">{blog.excerpt}</p>
                        <p className="text-gray-600 mb-3 text-sm line-clamp-3">{blog.content?.substring(0, 200)}...</p>
                        {blog.tags && (
                          <div className="mb-3">
                            {blog.tags.split(',').map((tag, index) => (
                              <span key={index} className="inline-block bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs mr-2 mb-1">
                                {tag.trim()}
                              </span>
                            ))}
                          </div>
                        )}
                        <div className="text-sm text-gray-500">
                          <p>Created: {new Date(blog.created_at).toLocaleDateString()}</p>
                          {blog.updated_at && blog.updated_at !== blog.created_at && (
                            <p>Updated: {new Date(blog.updated_at).toLocaleDateString()}</p>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;
