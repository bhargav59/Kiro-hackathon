import sqlite3

def add_react_blog():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    react_content = """React is a powerful JavaScript library for building user interfaces, developed by Facebook. This comprehensive guide covers installation, development setup, and production deployment strategies.

## Installation and Setup

### Create React App (Recommended for Beginners)
```bash
# Install Node.js (prerequisite)
# Download from https://nodejs.org or use package manager

# Create new React app
npx create-react-app my-app
cd my-app

# Start development server
npm start

# Build for production
npm run build
```

### Vite Setup (Modern Alternative)
```bash
# Create React app with Vite
npm create vite@latest my-react-app -- --template react
cd my-react-app

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Manual Setup with Webpack
```bash
# Initialize project
mkdir my-react-app && cd my-react-app
npm init -y

# Install React and ReactDOM
npm install react react-dom

# Install development dependencies
npm install -D @babel/core @babel/preset-react babel-loader
npm install -D webpack webpack-cli webpack-dev-server
npm install -D html-webpack-plugin css-loader style-loader
```

## Core Concepts

### Components and JSX
```jsx
// Functional Component
import React, { useState, useEffect } from 'react';

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUser() {
      try {
        const response = await fetch(`/api/users/${userId}`);
        const userData = await response.json();
        setUser(userData);
      } catch (error) {
        console.error('Error fetching user:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchUser();
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div className="user-profile">
      <img src={user.avatar} alt={user.name} />
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <div className="user-stats">
        <span>Posts: {user.postCount}</span>
        <span>Followers: {user.followerCount}</span>
      </div>
    </div>
  );
}

export default UserProfile;
```

### State Management with Hooks
```jsx
import React, { useState, useReducer, useContext, createContext } from 'react';

// Context for global state
const AppContext = createContext();

// Reducer for complex state logic
function appReducer(state, action) {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_THEME':
      return { ...state, theme: action.payload };
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [...state.notifications, action.payload]
      };
    default:
      return state;
  }
}

// App Provider Component
function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, {
    user: null,
    theme: 'light',
    notifications: []
  });

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

// Custom hook to use app context
function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}

// Component using global state
function Header() {
  const { state, dispatch } = useApp();

  const toggleTheme = () => {
    const newTheme = state.theme === 'light' ? 'dark' : 'light';
    dispatch({ type: 'SET_THEME', payload: newTheme });
  };

  return (
    <header className={`header ${state.theme}`}>
      <h1>My App</h1>
      {state.user && <span>Welcome, {state.user.name}</span>}
      <button onClick={toggleTheme}>
        Switch to {state.theme === 'light' ? 'dark' : 'light'} mode
      </button>
    </header>
  );
}
```

### Custom Hooks
```jsx
// Custom hook for API calls
function useApi(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch(url);
        if (!response.ok) throw new Error('Network response was not ok');
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [url]);

  return { data, loading, error };
}

// Custom hook for local storage
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  };

  return [storedValue, setValue];
}

// Usage example
function Settings() {
  const [preferences, setPreferences] = useLocalStorage('userPreferences', {
    theme: 'light',
    language: 'en'
  });

  const { data: user, loading } = useApi('/api/user/profile');

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Settings</h2>
      <label>
        Theme:
        <select
          value={preferences.theme}
          onChange={(e) => setPreferences({
            ...preferences,
            theme: e.target.value
          })}
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </label>
    </div>
  );
}
```

## Routing with React Router
```jsx
import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/users">Users</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/users" element={<UserList />} />
        <Route path="/users/:id" element={<UserDetail />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

// Protected Route Component
function ProtectedRoute({ children }) {
  const { state } = useApp();
  
  if (!state.user) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
}
```

## State Management with Redux Toolkit
```jsx
// store/userSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchUser = createAsyncThunk(
  'user/fetchUser',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/users/${userId}`);
      if (!response.ok) throw new Error('Failed to fetch user');
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const userSlice = createSlice({
  name: 'user',
  initialState: {
    data: null,
    loading: false,
    error: null
  },
  reducers: {
    clearUser: (state) => {
      state.data = null;
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

export const { clearUser } = userSlice.actions;
export default userSlice.reducer;

// store/index.js
import { configureStore } from '@reduxjs/toolkit';
import userReducer from './userSlice';

export const store = configureStore({
  reducer: {
    user: userReducer
  }
});
```

## Testing

### Jest and React Testing Library
```jsx
// UserProfile.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import UserProfile from './UserProfile';

// Mock API server
const server = setupServer(
  rest.get('/api/users/:id', (req, res, ctx) => {
    return res(ctx.json({
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      avatar: '/avatar.jpg'
    }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('UserProfile', () => {
  test('renders user information', async () => {
    render(<UserProfile userId="1" />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  test('handles API error', async () => {
    server.use(
      rest.get('/api/users/:id', (req, res, ctx) => {
        return res(ctx.status(404));
      })
    );

    render(<UserProfile userId="999" />);
    
    await waitFor(() => {
      expect(screen.getByText('User not found')).toBeInTheDocument();
    });
  });
});
```

## Performance Optimization

### Code Splitting and Lazy Loading
```jsx
import { lazy, Suspense } from 'react';

// Lazy load components
const Dashboard = lazy(() => import('./Dashboard'));
const UserProfile = lazy(() => import('./UserProfile'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<UserProfile />} />
      </Routes>
    </Suspense>
  );
}

// Memoization for expensive calculations
import { useMemo, memo } from 'react';

const ExpensiveComponent = memo(({ data, filter }) => {
  const filteredData = useMemo(() => {
    return data.filter(item => item.category === filter);
  }, [data, filter]);

  return (
    <div>
      {filteredData.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
});
```

## Production Deployment

### Build Optimization
```json
// package.json
{
  "scripts": {
    "build": "react-scripts build",
    "build:analyze": "npm run build && npx bundle-analyzer build/static/js/*.js"
  }
}
```

### Docker Deployment
```dockerfile
# Multi-stage build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Handle client-side routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

## Decision Framework
- **Project Size**: Small projects → Create React App
- **Performance**: Large apps → Vite or custom Webpack
- **State Complexity**: Simple → useState/useContext, Complex → Redux Toolkit
- **Team Size**: Large teams → TypeScript + strict linting
- **SEO Requirements**: Critical → Next.js (SSR/SSG)

React provides excellent developer experience with powerful ecosystem for building modern, interactive user interfaces."""
    
    cursor.execute('''
        INSERT INTO blogs (title, content, author)
        VALUES (?, ?, ?)
    ''', ("React Complete Guide: Modern Frontend Development Setup and Best Practices", react_content, "Frontend Engineering Team"))
    
    conn.commit()
    conn.close()
    print("Successfully added React comprehensive blog!")

if __name__ == "__main__":
    add_react_blog()
