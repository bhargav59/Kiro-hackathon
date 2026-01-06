# CloudEngineered Platform

The IMDb for Cloud Tools - A comprehensive platform for discovering, reviewing, and comparing DevOps and cloud engineering tools.

## 🚀 Features

- **Tool Discovery**: Search and filter through a curated database of DevOps tools
- **Detailed Reviews**: Community-driven reviews and ratings
- **Smart Comparisons**: AI-powered tool comparisons
- **User Profiles**: Personal tool stacks and favorites
- **Real-time Stats**: Live GitHub statistics and trends
- **Responsive Design**: Works seamlessly across all devices

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL/SQLite** - Database
- **JWT Authentication** - Secure user authentication
- **Pydantic** - Data validation using Python type annotations

### Frontend
- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Fast build tool
- **React Router** - Client-side routing

## 🏃‍♂️ Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Seed sample data:
```bash
python seed_data.py
```

5. Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📚 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints

- `GET /api/tools` - List all tools with search and filtering
- `GET /api/tools/{slug}` - Get tool details
- `POST /api/tools` - Create new tool (admin)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/tools/{id}/reviews` - Get tool reviews
- `POST /api/tools/{id}/reviews` - Create review (authenticated)

## 🎯 Core Features

### Tool Discovery
- Full-text search across tool names and descriptions
- Filter by category, license, and pricing model
- Sort by popularity, stars, or alphabetical order
- Grid and list view modes

### User Authentication
- Email/password registration and login
- JWT-based authentication
- Protected routes for authenticated features

### Reviews & Ratings
- 5-star rating system
- Rich text reviews
- User profiles with review history

### Responsive Design
- Mobile-first approach
- Dark mode support (planned)
- Accessibility compliant (WCAG 2.1 AA)

## 🔧 Development

### Project Structure

```
cloudengineered/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── seed_data.py        # Sample data seeding
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main React component
│   │   ├── main.tsx        # React entry point
│   │   └── index.css       # Tailwind CSS
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
└── README.md
```

### Database Schema

The application uses a simple but effective schema:

- **Tools**: Core tool information with GitHub stats
- **Users**: User accounts and profiles  
- **Reviews**: User reviews and ratings for tools

### Adding New Tools

Tools can be added via the API or by extending the `seed_data.py` script:

```python
{
    "name": "Tool Name",
    "description": "Tool description",
    "homepage_url": "https://example.com",
    "github_url": "https://github.com/user/repo",
    "category": "CI/CD",
    "license": "MIT",
    "pricing_model": "free"
}
```

## 🚀 Deployment

### Backend Deployment
- Deploy to Railway, Render, or Heroku
- Set environment variables for database and JWT secret
- Use PostgreSQL for production database

### Frontend Deployment
- Deploy to Vercel, Netlify, or similar
- Update API base URL for production
- Enable CORS for your domain

### Environment Variables

Backend:
```
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-jwt-secret-key
```

Frontend:
```
VITE_API_BASE_URL=https://your-api-domain.com
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎉 Acknowledgments

- Built for the Dynamous × Kiro Hackathon
- Inspired by the need for better DevOps tool discovery
- Community-driven approach to tool evaluation

---

**CloudEngineered** - Making DevOps tool discovery simple and community-driven.
