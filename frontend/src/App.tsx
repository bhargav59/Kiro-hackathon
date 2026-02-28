import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Star, LogOut, CreditCard } from 'lucide-react';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import NaturalLanguageQuery from './components/NaturalLanguageQuery';
import EnhancedComparison from './components/EnhancedComparison';
import DiscoverPage from './components/DiscoverPage';
import EnhancedToolDetailPage from './components/EnhancedToolDetailPage';
import EnhancedAuth from './components/EnhancedAuth';
import AdminPage from './components/AdminPage';
import AdminDashboard from './components/AdminDashboard';
import BlogDetailPage from './components/BlogDetailPage';
import SimpleToolsPage from './components/SimpleToolsPage';
import TestPage from './components/TestPage';
import ProfilePage from './components/ProfilePage';
// Payment components
import PricingPage from './components/PricingPage';
import SubscriptionManager from './components/SubscriptionManager';
import CheckoutSuccess from './components/CheckoutSuccess';
import EmailCaptureModal from './components/EmailCaptureModal';
import OnboardingFlow from './components/OnboardingFlow';
import SEOComparisonPage from './components/SEOComparisonPage';

// Analytics
import { initAnalytics, identifyUser, resetUser, trackEvent } from './analytics';

// API Base URL
import { API_BASE } from './config';

// Types
import { Tool, User } from './types';

// Auth Context
const AuthContext = React.createContext<{
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
}>({
  user: null,
  token: null,
  login: async () => { },
  register: async () => { },
  logout: () => { }
});

// Auth Provider
const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));

  useEffect(() => {
    initAnalytics();
  }, []);

  useEffect(() => {
    if (token) {
      fetchUser();
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/users/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        identifyUser(String(userData.id), { email: userData.email, username: userData.username });
      }
    } catch (error) {
      console.error('Failed to fetch user:', error);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
      trackEvent('login_completed', { method: 'email' });
    } else {
      throw new Error('Login failed');
    }
  };

  const register = async (email: string, username: string, password: string) => {
    const response = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, username, password })
    });

    if (!response.ok) {
      throw new Error('Registration failed');
    }
    trackEvent('signup_completed', { method: 'email' });
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    resetUser();
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Header Component
const Header: React.FC = () => {
  const { user, logout } = React.useContext(AuthContext);

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center space-x-2">
            <div className="flex items-center">
              <img src="/logo.png" alt="Logo" className="h-12" />
            </div>
          </Link>

          <nav className="flex items-center space-x-6">
            <Link to="/tools" className="text-gray-700 hover:text-blue-600">Tools</Link>
            <Link to="/admin" className="text-gray-700 hover:text-blue-600">Blogs</Link>
            <Link to="/discover" className="text-gray-700 hover:text-blue-600">Discover</Link>
            <Link to="/compare" className="text-gray-700 hover:text-blue-600">Compare</Link>
            <Link to="/ai-search" className="text-gray-700 hover:text-blue-600">🤖 AI Search</Link>
            <Link to="/analytics" className="text-gray-700 hover:text-blue-600">📊 Analytics</Link>
            <Link to="/pricing" className="text-gray-700 hover:text-blue-600 flex items-center gap-1">
              <CreditCard size={16} />
              Pricing
            </Link>

            {user ? (
              <div className="flex items-center space-x-4">
                <Link to="/profile" className="text-gray-700 hover:text-blue-600">Profile</Link>
                <span className="text-gray-700">Hi, {user.username}</span>
                <button onClick={logout} className="text-gray-500 hover:text-red-600">
                  <LogOut size={20} />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link to="/login" className="text-gray-700 hover:text-blue-600">Login</Link>
                <Link to="/register" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                  Sign Up
                </Link>
              </div>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
};

// Tool Card Component
const ToolCard: React.FC<{ tool: Tool }> = ({ tool }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">{tool.name}</h3>
          <span className="inline-block bg-blue-100 text-blue-800 text-sm px-2 py-1 rounded-full">
            {tool.category}
          </span>
        </div>
        <div className="flex items-center text-yellow-500">
          <Star size={16} className="fill-current" />
          <span className="ml-1 text-sm text-gray-600">{tool.github_stars}</span>
        </div>
      </div>

      <p className="text-gray-600 mb-4 line-clamp-3">{tool.description}</p>

      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-500 capitalize">{tool.pricing_model}</span>
        <Link
          to={`/tools/${tool.slug}`}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm"
        >
          View Details
        </Link>
      </div>
    </div>
  );
};

// Home Page
const HomePage: React.FC = () => {
  const [featuredTools, setFeaturedTools] = useState<Tool[]>([]);

  useEffect(() => {
    fetchFeaturedTools();
  }, []);

  const fetchFeaturedTools = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/tools?limit=6`);
      const tools = await response.json();
      setFeaturedTools(tools);
    } catch (error) {
      console.error('Failed to fetch featured tools:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-5xl font-bold mb-6">
              The IMDb for Cloud Tools
            </h1>
            <p className="text-xl mb-8 max-w-3xl mx-auto">
              Discover, review, and compare the best DevOps and cloud engineering tools.
              Make informed decisions with community-driven insights.
            </p>
            <div className="flex justify-center space-x-4">
              <Link to="/tools" className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100">
                Browse Tools
              </Link>
              <Link to="/discover" className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-10 py-4 rounded-xl font-bold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl">
                🔍 Discover Tools
              </Link>
              <Link to="/compare" className="border-2 border-white text-white px-10 py-4 rounded-xl font-bold hover:bg-white hover:text-blue-600 transition-all duration-200 shadow-lg">
                ⚖️ Compare Tools
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Featured Tools */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Featured Tools</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featuredTools.map((tool) => (
            <ToolCard key={tool.id} tool={tool} />
          ))}
        </div>
      </div>
    </div>
  );
};

// ProfilePage is now imported from ./components/ProfilePage

// Login Page
// Main App Component

// Main App
const AppContent: React.FC = () => {
  const { token } = React.useContext(AuthContext);
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/tools" element={<SimpleToolsPage />} />
            <Route path="/tools/:slug" element={<EnhancedToolDetailPage />} />
            <Route path="/discover" element={<DiscoverPage />} />
            <Route path="/compare" element={<EnhancedComparison />} />
            <Route path="/compare/:slug" element={<SEOComparisonPage />} />
            <Route path="/ai-search" element={<NaturalLanguageQuery />} />
            <Route path="/analytics" element={<AnalyticsDashboard />} />
            <Route path="/blog/:id" element={<BlogDetailPage />} />
            <Route path="/test" element={<TestPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/login" element={<EnhancedAuth />} />
            <Route path="/register" element={<EnhancedAuth />} />
            {/* Payment Routes */}
            <Route path="/pricing" element={<PricingPage />} />
            <Route path="/subscription" element={<SubscriptionManager />} />
            <Route path="/checkout/success" element={<CheckoutSuccess />} />
            {/* Admin Routes */}
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/blogs" element={<AdminPage />} />
          </Routes>
          <EmailCaptureModal />
          <OnboardingFlow token={token} />
        </div>
      </Router>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
