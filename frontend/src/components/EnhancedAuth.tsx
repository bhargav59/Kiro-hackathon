import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Mail, Lock, User, Github, Chrome, AlertCircle, CheckCircle } from 'lucide-react';

import { API_BASE } from '../config';

interface AuthProvider {
  name: string;
  display_name: string;
  icon: string;
  color: string;
}

const EnhancedAuth: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [providers, setProviders] = useState<AuthProvider[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    fetchProviders();
    
    // Handle OAuth callback
    const token = searchParams.get('token');
    const user = searchParams.get('user');
    const errorMessage = searchParams.get('message');
    
    if (token && user) {
      localStorage.setItem('token', token);
      localStorage.setItem('user', user);
      setSuccess(`Welcome back, ${user}!`);
      setTimeout(() => navigate('/'), 2000);
    } else if (errorMessage) {
      setError(errorMessage);
    }
  }, [searchParams, navigate]);

  const fetchProviders = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/auth/providers`);
      const data = await response.json();
      setProviders(data.providers || []);
    } catch (error) {
      console.error('Error fetching providers:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : { 
            username: formData.username, 
            email: formData.email, 
            password: formData.password 
          };

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok) {
        if (isLogin) {
          localStorage.setItem('token', data.access_token);
          localStorage.setItem('user', data.user.username);
          setSuccess('Login successful!');
          setTimeout(() => navigate('/'), 1500);
        } else {
          setSuccess('Registration successful! Please login.');
          setIsLogin(true);
          setFormData({ username: '', email: '', password: '', confirmPassword: '' });
        }
      } else {
        setError(data.detail || 'Authentication failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOAuthLogin = (provider: string) => {
    window.location.href = `${API_BASE}/api/auth/${provider}`;
  };

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case 'google': return <Chrome size={20} />;
      case 'github': return <Github size={20} />;
      default: return <User size={20} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <img src="/logo.png" alt="Logo" className="h-16" />
          </div>
          <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            {isLogin ? 'Welcome Back' : 'Join CloudEngineered'}
          </h2>
          <p className="mt-2 text-gray-600">
            {isLogin ? 'Sign in to your account' : 'Create your account to get started'}
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-2xl border border-gray-100 p-8">
          {/* Status Messages */}
          {error && (
            <div className="mb-6 bg-red-50 border-2 border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center">
              <AlertCircle size={20} className="mr-2" />
              {error}
            </div>
          )}

          {success && (
            <div className="mb-6 bg-green-50 border-2 border-green-200 text-green-700 px-4 py-3 rounded-xl flex items-center">
              <CheckCircle size={20} className="mr-2" />
              {success}
            </div>
          )}

          {/* OAuth Providers */}
          {providers.length > 0 && (
            <div className="mb-8">
              <div className="text-center mb-4">
                <span className="text-gray-500 text-sm">Continue with</span>
              </div>
              <div className="space-y-3">
                {providers.map((provider) => (
                  <button
                    key={provider.name}
                    onClick={() => handleOAuthLogin(provider.name)}
                    className={`w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-xl text-white font-medium ${provider.color} transition-all duration-200 hover:shadow-lg`}
                  >
                    {getProviderIcon(provider.name)}
                    <span className="ml-2">Continue with {provider.display_name}</span>
                  </button>
                ))}
              </div>
              
              <div className="mt-6 relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Or continue with email</span>
                </div>
              </div>
            </div>
          )}

          {/* Email/Password Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    required
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                    placeholder="Choose a username"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter your password"
                />
              </div>
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="password"
                    required
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                    className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                    placeholder="Confirm your password"
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  {isLogin ? 'Signing In...' : 'Creating Account...'}
                </div>
              ) : (
                isLogin ? 'Sign In' : 'Create Account'
              )}
            </button>
          </form>

          {/* Toggle Login/Register */}
          <div className="text-center mt-6">
            <button
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
                setSuccess('');
                setFormData({ username: '', email: '', password: '', confirmPassword: '' });
              }}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
            </button>
          </div>
        </div>

        {/* Features Preview */}
        <div className="text-center">
          <p className="text-gray-600 mb-4">Join thousands of developers using CloudEngineered</p>
          <div className="flex justify-center space-x-6 text-sm text-gray-500">
            <span>🔍 Discover Tools</span>
            <span>⚖️ Compare Features</span>
            <span>🤖 AI Search</span>
            <span>📊 Analytics</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedAuth;
