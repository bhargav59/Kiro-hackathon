import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import { Search, Star, Github, ExternalLink, User, LogOut } from 'lucide-react';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import NaturalLanguageQuery from './components/NaturalLanguageQuery';
import EnhancedComparison from './components/EnhancedComparison';
import DiscoverPage from './components/DiscoverPage';
import ReviewsSection from './components/ReviewsSection';
import EnhancedToolDetailPage from './components/EnhancedToolDetailPage';

// API Base URL
const API_BASE = 'http://localhost:8000';

// Types
interface Tool {
  id: number;
  name: string;
  slug: string;
  description: string;
  homepage_url?: string;
  github_url?: string;
  category: string;
  license?: string;
  pricing_model: string;
  github_stars: number;
  github_forks: number;
  ai_summary?: string;
  created_at: string;
}

interface User {
  id: number;
  email: string;
  username: string;
  avatar_url?: string;
  bio?: string;
  created_at: string;
}


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
  login: async () => {},
  register: async () => {},
  logout: () => {}
});

// Auth Provider
const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));

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
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
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
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">CE</span>
            </div>
            <span className="text-xl font-bold text-gray-900">CloudEngineered</span>
          </Link>
          
          <nav className="flex items-center space-x-6">
            <Link to="/tools" className="text-gray-700 hover:text-blue-600">Tools</Link>
            <Link to="/discover" className="text-gray-700 hover:text-blue-600">Discover</Link>
            <Link to="/compare" className="text-gray-700 hover:text-blue-600">Compare</Link>
            <Link to="/ai-search" className="text-gray-700 hover:text-blue-600">🤖 AI Search</Link>
            <Link to="/analytics" className="text-gray-700 hover:text-blue-600">📊 Analytics</Link>
            
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

// Tools Page
const ToolsPage: React.FC = () => {
  const [tools, setTools] = useState<Tool[]>([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');

  useEffect(() => {
    fetchTools();
  }, [search, category]);

  const fetchTools = async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (category) params.append('category', category);
      
      const response = await fetch(`${API_BASE}/api/tools?${params}`);
      const toolsData = await response.json();
      setTools(toolsData);
    } catch (error) {
      console.error('Failed to fetch tools:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <div className="flex-1 max-w-lg">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Search tools..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              <option value="CI/CD">CI/CD</option>
              <option value="Monitoring">Monitoring</option>
              <option value="Containerization">Containerization</option>
              <option value="Orchestration">Orchestration</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tools.map((tool) => (
            <ToolCard key={tool.id} tool={tool} />
          ))}
        </div>
      </div>
    </div>
  );
};

// Tool Detail Page
const ToolDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [tool, setTool] = useState<Tool | null>(null);

  useEffect(() => {
    if (slug) {
      fetchTool();
    }
  }, [slug]);

  const fetchTool = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/${slug}`);
      const toolData = await response.json();
      setTool(toolData);
    } catch (error) {
      console.error('Failed to fetch tool:', error);
    }
  };

  if (!tool) return <div className="flex justify-center items-center min-h-screen"><div className="text-lg">Loading...</div></div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">{tool.name}</h1>
          <p className="text-xl text-gray-600 mb-6">{tool.description}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">Details</h3>
              <div className="space-y-2">
                <div><strong>Category:</strong> {tool.category}</div>
                <div><strong>Stars:</strong> {tool.github_stars}</div>
                <div><strong>License:</strong> {tool.license || 'N/A'}</div>
                <div><strong>Pricing:</strong> {tool.pricing_model}</div>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Links</h3>
              <div className="space-y-2">
                {tool.homepage_url && (
                  <a href={tool.homepage_url} target="_blank" rel="noopener noreferrer" 
                     className="flex items-center space-x-2 text-blue-600 hover:text-blue-800">
                    <ExternalLink size={16} />
                    <span>Website</span>
                  </a>
                )}
                {tool.github_url && (
                  <a href={tool.github_url} target="_blank" rel="noopener noreferrer"
                     className="flex items-center space-x-2 text-blue-600 hover:text-blue-800">
                    <Github size={16} />
                    <span>GitHub</span>
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Reviews Section */}
        <ReviewsSection toolId={tool.id} toolName={tool.name} />
      </div>
    </div>
  );
};

// Profile Page
const ProfilePage: React.FC = () => {
  const { user } = React.useContext(AuthContext);

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Please log in to view your profile</h2>
          <Link to="/login" className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
            Log In
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Profile</h1>
          <div className="space-y-2">
            <div><strong>Username:</strong> {user.username}</div>
            <div><strong>Email:</strong> {user.email}</div>
            <div><strong>Member since:</strong> {new Date(user.created_at).toLocaleDateString()}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Login Page
const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = React.useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate('/');
    } catch (error) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-sm p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Login</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
          >
            Login
          </button>
        </form>
        
        <p className="mt-4 text-center text-gray-600">
          Don't have an account? <Link to="/register" className="text-blue-600 hover:text-blue-800">Sign up</Link>
        </p>
      </div>
    </div>
  );
};

// Register Page
const RegisterPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const { register } = React.useContext(AuthContext);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register(email, username, password);
      setSuccess(true);
    } catch (error) {
      setError('Registration failed');
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-sm p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Registration Successful!</h2>
          <p className="text-gray-600 mb-6">You can now log in with your credentials.</p>
          <Link to="/login" className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-sm p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Sign Up</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
          >
            Sign Up
          </button>
        </form>
        
        <p className="mt-4 text-center text-gray-600">
          Already have an account? <Link to="/login" className="text-blue-600 hover:text-blue-800">Login</Link>
        </p>
      </div>
    </div>
  );
};

// Main App
const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/tools" element={<ToolsPage />} />
            <Route path="/tools/:slug" element={<EnhancedToolDetailPage />} />
            <Route path="/discover" element={<DiscoverPage />} />
            <Route path="/compare" element={<EnhancedComparison />} />
            <Route path="/ai-search" element={<NaturalLanguageQuery />} />
            <Route path="/analytics" element={<AnalyticsDashboard />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
