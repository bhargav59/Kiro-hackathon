# CloudEngineered Platform

🏆 **The IMDb for DevOps Tools** - A comprehensive AI-powered platform for discovering, reviewing, and comparing DevOps and cloud engineering tools with professional blog management.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/bhargav59/Kiro-hackathon)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)

## 🚀 Features

### Core Platform
- **🤖 AI-Powered Comparisons**: Real-time tool analysis using Google Gemini
- **🔍 Intelligent Tool Discovery**: Search with natural language queries
- **⭐ Community Reviews**: 5-star rating system with detailed reviews
- **🔐 Complete Authentication**: OAuth (Google/GitHub) + traditional login + forgot password
- **👤 User Profiles**: Personal tool stacks and preferences
- **📊 Real-time Analytics**: Live GitHub statistics and platform insights
- **📱 Responsive Design**: Mobile-first, accessibility compliant

### Professional Blog System
- **📝 Admin Dashboard**: Complete blog management interface
- **✍️ Rich Content Editor**: Professional blog creation with categories and tags
- **📚 Expert Content**: 10 pre-loaded professional DevOps articles
- **🔒 Secure Access**: Authentication-protected admin features
- **📈 Analytics**: View tracking and engagement metrics

### Advanced Features
- **🌐 Natural Language Search**: "Find me a Docker alternative for containers"
- **🔄 Multi-tool Comparisons**: Side-by-side analysis with AI insights
- **📈 Trend Analysis**: Tool popularity and adoption tracking
- **🎯 Smart Recommendations**: AI-powered tool suggestions

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework with automatic API docs
- **SQLAlchemy** - SQL toolkit and ORM with SQLite/PostgreSQL support
- **JWT Authentication** - Secure token-based authentication
- **bcrypt** - Password hashing and security
- **Google Gemini AI** - Advanced AI-powered comparisons
- **Pydantic** - Data validation and serialization

### Frontend
- **React 18** - Modern React with hooks and concurrent features
- **TypeScript** - Type-safe JavaScript development
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Fast build tool with hot module replacement
- **React Router** - Client-side routing and navigation

### Database
- **SQLite** (Development) - Lightweight, file-based database
- **PostgreSQL** (Production) - Scalable relational database
- **Comprehensive Schema** - Users, blogs, tools, reviews, authentication

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** - [Download Python](https://python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/)
- **Google Gemini API Key** (Optional) - [Get API Key](https://makersuite.google.com/app/apikey)

### 1. Clone Repository
```bash
git clone https://github.com/bhargav59/Kiro-hackathon.git
cd Kiro-hackathon
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_simple.txt

# Optional: Set up AI features
export GEMINI_API_KEY='your-api-key-here'

# Start the backend server
python blog_main.py
```

The backend API will be available at `http://localhost:8000`

### 3. Frontend Setup
```bash
# Navigate to frontend directory (in new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 4. Access the Platform
- **Main Platform**: http://localhost:3000
- **Admin Dashboard**: http://localhost:3000/admin
- **API Documentation**: http://localhost:8000/docs

## 🔧 Detailed Setup Instructions

### Backend Configuration

#### Environment Variables
Create a `.env` file in the `backend` directory:
```env
# Optional: AI Features
GEMINI_API_KEY=your-gemini-api-key

# Optional: Database (defaults to SQLite)
DATABASE_URL=sqlite:///./blog.db

# Optional: JWT Secret (auto-generated if not set)
SECRET_KEY=your-secret-key-here
```

#### Database Initialization
The database is automatically created on first run. To seed with professional blog content:
```bash
cd backend
source venv/bin/activate
python seed_professional_blogs.py
python seed_remaining_blogs.py
```

### Frontend Configuration

#### API Configuration
Update `frontend/src/config.ts` if needed:
```typescript
export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

#### Build for Production
```bash
cd frontend
npm run build
```

## 🐳 Docker Deployment

### Quick Docker Setup
```bash
# Build and run with Docker
docker build -f Dockerfile.simple -t cloudengineered .
docker run -d -p 8000:8000 --name cloudengineered cloudengineered

# Frontend (separate container or serve static files)
cd frontend && npm run build
# Serve dist/ folder with nginx or similar
```

### Docker Compose (Recommended)
```yaml
version: '3.8'
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.simple
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./backend/blog.db:/app/blog.db
  
  frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

## 🚀 Production Deployment

### Backend Deployment Options

#### 1. Railway/Render/Heroku
```bash
# Set environment variables
GEMINI_API_KEY=your-api-key
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-jwt-secret

# Deploy backend files
git push origin main
```

#### 2. VPS/Cloud Server
```bash
# Install dependencies
sudo apt update && sudo apt install python3 python3-pip nginx

# Clone and setup
git clone https://github.com/bhargav59/Kiro-hackathon.git
cd Kiro-hackathon/backend
pip install -r requirements_simple.txt

# Run with gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker blog_main:app --bind 0.0.0.0:8000
```

### Frontend Deployment Options

#### 1. Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

#### 2. Netlify
```bash
# Build and deploy
cd frontend
npm run build
# Upload dist/ folder to Netlify
```

#### 3. Static Hosting
```bash
cd frontend
npm run build
# Serve dist/ folder with any static hosting service
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password with token
- `GET /api/auth/me` - Get current user info

### Blog Management Endpoints
- `GET /api/blogs` - List all blog posts
- `POST /api/blogs` - Create new blog post (authenticated)
- `GET /api/blogs/{id}` - Get specific blog post
- `PUT /api/blogs/{id}` - Update blog post (authenticated)
- `DELETE /api/blogs/{id}` - Delete blog post (authenticated)

### Tool Discovery Endpoints
- `GET /api/tools` - List all tools with filtering
- `GET /api/analytics/overview` - Platform analytics
- `POST /api/ai/enhanced-compare` - AI-powered tool comparison

## 🎯 Usage Guide

### Admin Dashboard Access
1. Navigate to `http://localhost:3000/admin`
2. Sign up for a new account or login
3. Access blog management features
4. Create, edit, and delete blog posts

### Blog Management
- **Create Posts**: Rich editor with title, excerpt, content, categories, and tags
- **Edit Posts**: Inline editing with save/cancel options
- **Delete Posts**: One-click deletion with confirmation
- **View Analytics**: Track views and engagement

### Tool Discovery
- **Search Tools**: Use natural language or keyword search
- **Compare Tools**: Select multiple tools for AI-powered comparison
- **View Analytics**: Real-time platform statistics

## 📂 .kiro/ Documentation

This project includes comprehensive Kiro CLI documentation in the `.kiro/` directory:

| File | Description |
|------|-------------|
| `.kiro/steering/global_rules.md` | Architecture principles, coding standards, and quality gates |
| `.kiro/steering/PRD.md` | Product Requirements Document with features and success metrics |
| `.kiro/steering/architecture.md` | Technical architecture and design decisions |
| `.kiro/prompts/custom_commands.md` | Reusable development workflow commands |
| `.kiro/prompts/workflows.md` | Automation and deployment workflows |
| `.kiro/subagents/configuration.md` | Subagent delegation patterns and usage examples |
| `.kiro/DEVLOG.md` | Development log with timeline, decisions, and lessons learned |

### Key Documentation Highlights

- **Global Rules**: Defines AI-first design, component-driven development, and security standards
- **PRD**: Covers intelligent tool discovery, AI comparisons, OAuth authentication, and analytics
- **Subagents**: Configures data-enhancer, ai-processor, frontend-developer, and backend-developer agents
- **DEVLOG**: Documents 35+ hours of development across 4 days with all technical decisions

## 🔧 Development


### Project Structure
```
cloudengineered/
├── .kiro/                       # Kiro CLI configurations & documentation
│   ├── steering/               # Strategic documents
│   │   ├── global_rules.md    # Architecture principles & coding standards
│   │   ├── PRD.md             # Product Requirements Document
│   │   └── architecture.md    # Technical architecture
│   ├── prompts/                # Reusable prompts
│   │   ├── custom_commands.md # Development workflow commands
│   │   └── workflows.md       # Automation workflows
│   ├── subagents/              # Subagent configurations
│   │   └── configuration.md   # Agent delegation patterns
│   └── DEVLOG.md               # Development log & decisions
├── backend/
│   ├── blog_main.py            # Main FastAPI application
│   ├── oauth_service.py        # OAuth 2.0 (GitHub/Google)
│   ├── backup_service.py       # Database autobackup system
│   ├── auth_utils.py           # Authentication utilities
│   ├── ai_blog_service.py      # AI-powered blog generation
│   ├── stripe_service.py       # Payment integration
│   ├── requirements.txt        # Python dependencies
│   └── blog.db                 # SQLite database (auto-created)
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── ProfilePage.tsx    # User profile page
│   │   │   ├── EnhancedAuth.tsx   # OAuth login UI
│   │   │   ├── AdminDashboard.tsx # Admin panel
│   │   │   └── ...
│   │   ├── App.tsx             # Main application
│   │   └── config.ts           # Configuration
│   ├── package.json            # Node.js dependencies
│   └── dist/                   # Built files (after npm run build)
├── Dockerfile.simple           # Docker configuration
└── README.md                   # This file
```

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Blogs table
CREATE TABLE blogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Password reset tokens
CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### Adding New Features
1. **Backend**: Add endpoints in `blog_main.py`
2. **Frontend**: Create components in `src/components/`
3. **Database**: Update schema and create migration scripts
4. **Documentation**: Update README and API docs

## 🧪 Testing

### Backend Testing
```bash
cd backend
source venv/bin/activate

# Test API endpoints
curl http://localhost:8000/api/blogs
curl http://localhost:8000/api/auth/register -X POST -H "Content-Type: application/json" -d '{"username":"test","email":"test@example.com","password":"test123"}'
```

### Frontend Testing
```bash
cd frontend

# Type checking
npx tsc --noEmit

# Build test
npm run build

# Development server
npm run dev
```

## 🔒 Security Features

- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Secure authentication with expiration
- **Password Reset**: Secure token-based password reset
- **Input Validation**: Comprehensive data validation
- **CORS Configuration**: Proper cross-origin resource sharing
- **SQL Injection Protection**: ORM-based database queries

## 📊 Performance

- **API Response Time**: < 200ms for most endpoints
- **Frontend Load Time**: < 2 seconds initial load
- **Database Queries**: Optimized with proper indexing
- **Caching**: Strategic caching for improved performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow TypeScript strict mode
- Use Tailwind CSS for styling
- Write comprehensive error handling
- Update documentation for new features
- Test all API endpoints

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 Acknowledgments

- **Dynamous × Kiro Hackathon** - Platform and inspiration
- **Google Gemini AI** - Advanced AI capabilities
- **Open Source Community** - Tools and libraries used
- **DevOps Community** - Inspiration for tool discovery needs

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/bhargav59/Kiro-hackathon/issues)
- **Documentation**: Check the `.kiro/` directory for detailed documentation
- **API Docs**: Visit `http://localhost:8000/docs` when running locally

---

**CloudEngineered** - Making DevOps tool discovery simple, intelligent, and community-driven.

Built with ❤️ using Kiro CLI and modern web technologies.
