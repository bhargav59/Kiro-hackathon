from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
import httpx
from oauth_config import oauth, get_oauth_providers
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr, Field
import requests
import json
from datetime import datetime, timedelta
from typing import List, Optional
import jwt
import bcrypt
import os
import secrets
import logging
from contextlib import contextmanager
import asyncio
import aiohttp
import google.generativeai as genai
from tool_knowledge import TOOL_KNOWLEDGE, get_tool_data, calculate_roi
from auth_utils import get_secret_key, validate_password_strength, login_rate_limiter

logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cloudengineered.db")

# Configure engine with proper settings for SQLite vs PostgreSQL
_engine_kwargs: dict = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs["pool_size"] = 10
    _engine_kwargs["max_overflow"] = 20

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Tool(Base):
    __tablename__ = "tools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    slug = Column(String, unique=True, index=True)
    description = Column(Text)
    homepage_url = Column(String)
    github_url = Column(String)
    category = Column(String)
    license = Column(String)
    pricing_model = Column(String)
    logo_url = Column(String)
    github_stars = Column(Integer, default=0)
    github_forks = Column(Integer, default=0)
    last_commit_date = Column(DateTime)
    ai_summary = Column(Text)
    health_score = Column(Integer, default=0)
    health_data = Column(Text)  # JSON blob with score breakdown
    last_health_check = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    reviews = relationship("Review", back_populates="tool")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    github_id = Column(String)
    oauth_provider = Column(String, nullable=True)  # 'google', 'github', or None
    avatar_url = Column(String)
    bio = Column(Text)
    is_admin = Column(Boolean, default=False)
    subscription_plan = Column(String, default="free")  # free, pro, enterprise
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reviews = relationship("Review", back_populates="user")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("tools.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)
    content = Column(Text)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    tool = relationship("Tool", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

class UserStack(Base):
    __tablename__ = "user_stacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tool_id = Column(Integer, ForeignKey("tools.id"))
    added_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    tool = relationship("Tool")

class ReviewVote(Base):
    __tablename__ = "review_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    is_helpful = Column(Boolean, default=True)

class Blog(Base):
    __tablename__ = "blogs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    author = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, index=True)  # "comparisons", "exports", "ai_searches"
    created_at = Column(DateTime, default=datetime.utcnow)

class EmailSubscriber(Base):
    __tablename__ = "email_subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    source = Column(String)  # "homepage", "comparison", "blog", "register"
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ComparisonPage(Base):
    __tablename__ = "comparison_pages"

    id = Column(Integer, primary_key=True, index=True)
    tool_a_id = Column(Integer, ForeignKey("tools.id"))
    tool_b_id = Column(Integer, ForeignKey("tools.id"))
    slug = Column(String, unique=True, index=True)
    title = Column(String)
    content = Column(Text)
    meta_description = Column(String)
    views = Column(Integer, default=0)
    generated_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    tool_a = relationship("Tool", foreign_keys=[tool_a_id])
    tool_b = relationship("Tool", foreign_keys=[tool_b_id])

# Pydantic models
class ToolCreate(BaseModel):
    name: str
    description: str
    homepage_url: Optional[str] = None
    github_url: Optional[str] = None
    category: str
    license: Optional[str] = None
    pricing_model: str = "free"

class ToolResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    homepage_url: Optional[str]
    github_url: Optional[str]
    category: str
    license: Optional[str]
    pricing_model: str
    github_stars: int
    github_forks: int
    ai_summary: Optional[str]
    health_score: Optional[int] = 0
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    avatar_url: Optional[str]
    bio: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    content: str = Field(..., min_length=1, max_length=5000)

class ReviewResponse(BaseModel):
    id: int
    rating: int
    content: str
    helpful_count: int
    created_at: datetime
    user: UserResponse
    
    class Config:
        from_attributes = True

class UserStackResponse(BaseModel):
    id: int
    tool: ToolResponse
    added_at: datetime
    
    class Config:
        from_attributes = True

class CompareRequest(BaseModel):
    tool_ids: List[int]

class LoginRequest(BaseModel):
    email: str
    password: str

class BlogCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=200)

class Token(BaseModel):
    access_token: str
    token_type: str

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="CloudEngineered API", version="1.0.0")

# Add session middleware for OAuth - require SECRET_KEY in production
_session_secret = os.getenv("SECRET_KEY")
if not _session_secret:
    if os.getenv("ENV", "development") == "production":
        raise RuntimeError("SECRET_KEY environment variable is required in production")
    _session_secret = secrets.token_urlsafe(32)
    logger.warning("SECRET_KEY not set - using random key (sessions won't persist across restarts)")
app.add_middleware(SessionMiddleware, secret_key=_session_secret)

# CORS configuration - restrict origins (set CORS_ORIGINS env var in production)
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        if os.getenv("ENV") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Security
security = HTTPBearer()
SECRET_KEY = get_secret_key()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Configure Gemini AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# In-memory store for OAuth auth codes (short-lived, exchanged for tokens)
_pending_auth_codes: dict = {}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({
        "exp": expire,
        "iss": "cloudengineered",
        "aud": "cloudengineered-api",
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=["HS256"],
            audience="cloudengineered-api", issuer="cloudengineered",
            options={"verify_sub": False}
        )
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = int(user_id_raw)
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_admin_user(current_user: User = Depends(get_current_user)):
    """Require admin role for admin endpoints"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def create_slug(name: str) -> str:
    return name.lower().replace(" ", "-").replace(".", "").replace("/", "-")

async def fetch_github_stats(github_url: str) -> dict:
    """Fetch GitHub statistics for a repository"""
    if not github_url or "github.com" not in github_url:
        return {"stars": 0, "forks": 0, "last_commit": None}
    
    try:
        # Extract owner/repo from GitHub URL
        parts = github_url.replace("https://github.com/", "").split("/")
        if len(parts) < 2:
            return {"stars": 0, "forks": 0, "last_commit": None}
        
        owner, repo = parts[0], parts[1]
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "stars": data.get("stargazers_count", 0),
                        "forks": data.get("forks_count", 0),
                        "last_commit": data.get("updated_at")
                    }
    except Exception as e:
        logger.error(f"Error fetching GitHub stats: {e}")
    
    return {"stars": 0, "forks": 0, "last_commit": None}

async def generate_ai_comparison(tools: List[Tool]) -> dict:
    """Generate AI-powered tool comparison using Gemini"""
    if not GEMINI_API_KEY:
        # Fallback to mock comparison
        return generate_mock_comparison(tools)
    
    try:
        model = genai.GenerativeModel('models/gemini-3-flash-preview')
        
        # Create comparison prompt
        tool_info = []
        for tool in tools:
            info = f"""
Tool: {tool.name}
Category: {tool.category}
Description: {tool.description}
GitHub Stars: {tool.github_stars}
License: {tool.license or 'Unknown'}
Pricing: {tool.pricing_model}
"""
            tool_info.append(info)
        
        prompt = f"""
Compare these DevOps/Cloud tools and provide a detailed analysis:

{chr(10).join(tool_info)}

Please provide a JSON response with the following structure:
{{
    "summary": "Brief comparison summary",
    "strengths": {{
        "Tool1": "Key strengths",
        "Tool2": "Key strengths"
    }},
    "use_cases": {{
        "Tool1": "Best use cases",
        "Tool2": "Best use cases"
    }},
    "pros_cons": {{
        "Tool1": {{"pros": ["pro1", "pro2"], "cons": ["con1", "con2"]}},
        "Tool2": {{"pros": ["pro1", "pro2"], "cons": ["con1", "con2"]}}
    }},
    "recommendations": "Which tool to choose when and why"
}}

Focus on practical differences, performance, learning curve, and ecosystem.
"""
        
        response = model.generate_content(prompt)
        
        # Parse JSON from response
        try:
            # Extract JSON from response text
            response_text = response.text
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            comparison_data = json.loads(json_text)
            return comparison_data
            
        except json.JSONDecodeError:
            # If JSON parsing fails, create structured response from text
            return {
                "summary": response.text[:200] + "...",
                "strengths": {tool.name: f"Excels in {tool.category.lower()}" for tool in tools},
                "use_cases": {tool.name: f"Best for {tool.category.lower()} workflows" for tool in tools},
                "recommendations": "Choose based on your specific requirements and team expertise."
            }
            
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return generate_mock_comparison(tools)

def generate_mock_comparison(tools: List[Tool]) -> dict:
    """Fallback mock comparison"""
    return {
        "summary": f"Comparing {len(tools)} tools across different categories and use cases.",
        "strengths": {tool.name: f"Excels in {tool.category.lower()} with {tool.github_stars} GitHub stars" for tool in tools},
        "use_cases": {tool.name: f"Best for teams focusing on {tool.category.lower()} workflows" for tool in tools},
        "recommendations": "Choose based on your specific requirements and team expertise."
    }
def generate_ai_summary(tool_name: str, description: str, category: str) -> str:
    """Generate AI summary for a tool (mock implementation)"""
    summaries = {
        "CI/CD": f"{tool_name} streamlines continuous integration and deployment workflows, enabling automated testing and reliable software delivery.",
        "Monitoring": f"{tool_name} provides comprehensive monitoring and observability capabilities for modern applications and infrastructure.",
        "Container": f"{tool_name} simplifies containerization and orchestration, making application deployment more consistent and scalable.",
        "Infrastructure": f"{tool_name} enables infrastructure as code practices, allowing teams to manage and provision resources programmatically."
    }
    
    base_summary = summaries.get(category, f"{tool_name} is a powerful tool in the {category} category.")
    return f"{base_summary} {description[:100]}..."

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for container orchestration"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")

# Routes
@app.get("/")
def read_root():
    return {"message": "CloudEngineered API", "version": "1.0.0"}

@app.get("/api/auth/providers")
async def get_auth_providers():
    """Get available OAuth providers"""
    return {"providers": get_oauth_providers()}

@app.get("/api/auth/{provider}")
async def oauth_login(provider: str, request: Request):
    """Initiate OAuth login"""
    if provider not in ['google', 'github']:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    
    client = oauth.create_client(provider)
    redirect_uri = f"{BACKEND_URL}/api/auth/{provider}/callback"
    return await client.authorize_redirect(request, redirect_uri)

@app.get("/api/auth/{provider}/callback")
async def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    """Handle OAuth callback"""
    if provider not in ['google', 'github']:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    
    try:
        client = oauth.create_client(provider)
        token = await client.authorize_access_token(request)
        
        if provider == 'google':
            user_info = token.get('userinfo')
            if not user_info:
                user_info = await client.parse_id_token(token)
            
            email = user_info.get('email')
            name = user_info.get('name')
            avatar_url = user_info.get('picture')
            
        elif provider == 'github':
            # Get user info from GitHub API
            async with httpx.AsyncClient() as http_client:
                headers = {'Authorization': f"token {token['access_token']}"}
                
                # Get user profile
                user_response = await http_client.get('https://api.github.com/user', headers=headers)
                user_data = user_response.json()
                
                # Get user email (might be private)
                email_response = await http_client.get('https://api.github.com/user/emails', headers=headers)
                emails = email_response.json()
                primary_email = next((e['email'] for e in emails if e['primary']), None)
                
                email = primary_email or user_data.get('email')
                name = user_data.get('name') or user_data.get('login')
                avatar_url = user_data.get('avatar_url')
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not available from provider")
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user
            user = User(
                username=name or email.split('@')[0],
                email=email,
                password_hash="",  # OAuth users don't have passwords
                oauth_provider=provider,
                avatar_url=avatar_url
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update OAuth info if needed
            if not user.oauth_provider:
                user.oauth_provider = provider
                user.avatar_url = avatar_url or user.avatar_url
                db.commit()
        
        # Create JWT token
        access_token = create_access_token({"sub": str(user.id)})

        # Use a short-lived auth code instead of passing JWT directly in URL
        # The frontend will exchange this code for the token via a POST request
        auth_code = secrets.token_urlsafe(32)
        _pending_auth_codes[auth_code] = {
            "token": access_token,
            "username": user.username,
            "expires": datetime.utcnow() + timedelta(minutes=5)
        }

        # Redirect to frontend with auth code (not the JWT itself)
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/callback?code={auth_code}",
            status_code=302
        )

    except Exception as e:
        logger.error(f"OAuth error: {e}", exc_info=True)
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/error?message=Authentication failed",
            status_code=302
        )

@app.post("/api/auth/exchange-code")
def exchange_auth_code(code_data: dict):
    """Exchange short-lived OAuth auth code for JWT token"""
    code = code_data.get("code", "")
    if not code or code not in _pending_auth_codes:
        raise HTTPException(status_code=400, detail="Invalid or expired auth code")

    entry = _pending_auth_codes.pop(code)
    if datetime.utcnow() > entry["expires"]:
        raise HTTPException(status_code=400, detail="Auth code expired")

    return {
        "access_token": entry["token"],
        "token_type": "bearer",
        "username": entry["username"]
    }

@app.post("/api/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Validate password strength
    is_valid, error_msg = validate_password_strength(user.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Check if user exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Hash password
    password_hash = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create user
    db_user = User(
        email=user.email,
        username=user.username,
        password_hash=password_hash
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/api/auth/login", response_model=Token)
def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    is_limited, reset_in = login_rate_limiter.is_rate_limited(client_ip)
    if is_limited:
        raise HTTPException(
            status_code=429,
            detail=f"Too many login attempts. Try again in {reset_in} seconds."
        )
    login_rate_limiter.record_attempt(client_ip)
    
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not bcrypt.checkpw(login_data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Reset rate limiter on successful login
    login_rate_limiter.reset(client_ip)
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/tools", response_model=List[ToolResponse])
def get_tools(skip: int = 0, limit: int = 20, search: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Tool)
    
    if search:
        query = query.filter(Tool.name.contains(search) | Tool.description.contains(search))
    if category:
        query = query.filter(Tool.category == category)
    
    tools = query.offset(skip).limit(limit).all()
    return tools

@app.get("/api/tools/{slug}", response_model=ToolResponse)
def get_tool(slug: str, db: Session = Depends(get_db)):
    tool = db.query(Tool).filter(Tool.slug == slug).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

@app.get("/api/tools/{tool_id}/reviews", response_model=List[ReviewResponse])
def get_tool_reviews(tool_id: int, db: Session = Depends(get_db)):
    """Get reviews for a specific tool"""
    reviews = db.query(Review).filter(Review.tool_id == tool_id).all()
    return reviews

@app.post("/api/tools/{tool_id}/reviews", response_model=ReviewResponse)
def create_review(tool_id: int, review: ReviewCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a review for a tool"""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    existing_review = db.query(Review).filter(Review.tool_id == tool_id, Review.user_id == current_user.id).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this tool")
    
    db_review = Review(
        tool_id=tool_id,
        user_id=current_user.id,
        rating=review.rating,
        content=review.content
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@app.post("/api/tools", response_model=ToolResponse)
async def create_tool(tool: ToolCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    slug = create_slug(tool.name)
    
    # Check if tool exists
    if db.query(Tool).filter(Tool.slug == slug).first():
        raise HTTPException(status_code=400, detail="Tool already exists")
    
    # Fetch GitHub stats if GitHub URL provided
    github_stats = await fetch_github_stats(tool.github_url) if tool.github_url else {"stars": 0, "forks": 0, "last_commit": None}
    
    # Generate AI summary
    ai_summary = generate_ai_summary(tool.name, tool.description, tool.category)
    
    db_tool = Tool(
        name=tool.name,
        slug=slug,
        description=tool.description,
        homepage_url=tool.homepage_url,
        github_url=tool.github_url,
        category=tool.category,
        license=tool.license,
        pricing_model=tool.pricing_model,
        github_stars=github_stats["stars"],
        github_forks=github_stats["forks"],
        last_commit_date=datetime.fromisoformat(github_stats["last_commit"].replace("Z", "+00:00")) if github_stats["last_commit"] else None,
        ai_summary=ai_summary
    )
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    
    return db_tool

@app.get("/api/users/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/api/ai/compare")
async def compare_tools(request: CompareRequest, db: Session = Depends(get_db)):
    """Generate AI-powered tool comparison with detailed matrix"""
    try:
        tools = db.query(Tool).filter(Tool.id.in_(request.tool_ids)).all()
        
        if len(tools) < 2:
            raise HTTPException(status_code=400, detail="At least 2 tools required for comparison")
        
        comparison = await generate_ai_comparison(tools)
        
        # Add comprehensive comparison features
        comparison["comparison_matrix"] = {
            "features": {
                "GitHub Stars": {tool.name: tool.github_stars for tool in tools},
                "License": {tool.name: tool.license for tool in tools},
                "Pricing": {tool.name: tool.pricing_model for tool in tools},
                "Category": {tool.name: tool.category for tool in tools}
            },
            "side_by_side": [
                {
                    "name": tool.name,
                    "stars": tool.github_stars,
                    "license": tool.license,
                    "pricing": tool.pricing_model,
                    "category": tool.category,
                    "description": tool.description[:200] + "..."
                } for tool in tools
            ],
            "export_options": ["PDF", "Markdown", "JSON"],
            "performance_metrics": {tool.name: {"popularity": tool.github_stars, "activity": "High"} for tool in tools}
        }
    
        return comparison

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compare_tools: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Comparison failed")

@app.get("/api/ai/recommendations")
def get_ai_recommendations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get AI-powered tool recommendations for the authenticated user"""
    # Get user's current stack
    user_tools = db.query(UserStack).filter(UserStack.user_id == current_user.id).all()
    user_categories = [tool.tool.category for tool in user_tools]

    # Recommend complementary tools
    all_tools = db.query(Tool).all()
    recommendations = []

    for tool in all_tools:
        if tool.category not in user_categories:
            recommendations.append({
                "tool": tool,
                "reason": f"Complements your {', '.join(user_categories)} stack",
                "confidence": 0.8
            })

    return {"recommendations": recommendations[:5], "based_on": "user_stack_analysis"}

@app.post("/api/ai/moderate")
def moderate_content(content: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """AI content moderation for reviews"""
    text = content.get("text", "")
    
    # Simple moderation rules
    spam_keywords = ["spam", "fake", "scam", "buy now", "click here"]
    inappropriate_words = ["hate", "offensive", "inappropriate"]
    
    is_spam = any(keyword in text.lower() for keyword in spam_keywords)
    is_inappropriate = any(word in text.lower() for word in inappropriate_words)
    
    return {
        "is_approved": not (is_spam or is_inappropriate),
        "is_spam": is_spam,
        "is_inappropriate": is_inappropriate,
        "confidence": 0.9,
        "suggested_action": "approve" if not (is_spam or is_inappropriate) else "review"
    }

@app.get("/api/tools/{tool_id}/recommendations")
def get_tool_recommendations(tool_id: int, db: Session = Depends(get_db)):
    """Get AI-powered tool recommendations"""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Get similar tools in same category
    similar_tools = db.query(Tool).filter(
        Tool.category == tool.category,
        Tool.id != tool_id
    ).limit(3).all()
    
    return {
        "similar_tools": [{"id": t.id, "name": t.name, "stars": t.github_stars} for t in similar_tools],
        "message": f"Tools similar to {tool.name} in the {tool.category} category"
    }

# User Stack endpoints
@app.get("/api/users/me/stack", response_model=List[UserStackResponse])
def get_user_stack(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's tool stack"""
    stacks = db.query(UserStack).filter(UserStack.user_id == current_user.id).all()
    return stacks

@app.post("/api/users/me/stack/{tool_id}")
def add_to_stack(tool_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add tool to user's stack"""
    # Check if tool exists
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Check if already in stack
    existing = db.query(UserStack).filter(UserStack.user_id == current_user.id, UserStack.tool_id == tool_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tool already in stack")
    
    stack_item = UserStack(user_id=current_user.id, tool_id=tool_id)
    db.add(stack_item)
    db.commit()
    return {"message": "Tool added to stack"}

@app.delete("/api/users/me/stack/{tool_id}")
def remove_from_stack(tool_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Remove tool from user's stack"""
    stack_item = db.query(UserStack).filter(UserStack.user_id == current_user.id, UserStack.tool_id == tool_id).first()
    if not stack_item:
        raise HTTPException(status_code=404, detail="Tool not in stack")
    
    db.delete(stack_item)
    db.commit()
    return {"message": "Tool removed from stack"}

@app.put("/api/tools/{tool_id}/enhance")
async def enhance_tool_details(tool_id: int, db: Session = Depends(get_db)):
    """Enhance tool details with real-time GitHub data and comprehensive information"""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Fetch real-time GitHub stats
    if tool.github_url:
        github_stats = await fetch_github_stats(tool.github_url)
        tool.github_stars = github_stats["stars"]
        tool.github_forks = github_stats["forks"]
        if github_stats["last_commit"]:
            tool.last_commit_date = datetime.fromisoformat(github_stats["last_commit"].replace("Z", "+00:00"))
    
    # Enhanced descriptions for popular tools
    enhanced_details = {
        "docker": {
            "description": "A comprehensive containerization platform that enables developers to package applications and their dependencies into lightweight, portable containers. Docker simplifies application deployment, scaling, and management across different environments while ensuring consistency from development to production.",
            "ai_summary": "Docker revolutionized software deployment through containerization, enabling consistent environments across development, testing, and production. It provides container orchestration, image management, and seamless integration with CI/CD pipelines. Docker's ecosystem includes Docker Hub for image sharing, Docker Compose for multi-container applications, and Docker Swarm for orchestration. Key benefits include resource efficiency, rapid deployment, microservices architecture support, and cross-platform compatibility."
        },
        "kubernetes": {
            "description": "An open-source container orchestration platform that automates deployment, scaling, and management of containerized applications. Kubernetes provides service discovery, load balancing, storage orchestration, automated rollouts and rollbacks, and self-healing capabilities for distributed systems.",
            "ai_summary": "Kubernetes is the de facto standard for container orchestration, providing powerful features for scaling, service discovery, and managing complex distributed applications. It offers declarative configuration, horizontal pod autoscaling, rolling updates, and extensive ecosystem integration. K8s excels in microservices architectures, multi-cloud deployments, and enterprise-grade container management."
        }
    }
    
    tool_key = tool.name.lower()
    if tool_key in enhanced_details:
        tool.description = enhanced_details[tool_key]["description"]
        tool.ai_summary = enhanced_details[tool_key]["ai_summary"]
    
    tool.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tool)
    
    return tool

# Review voting endpoints
@app.post("/api/reviews/{review_id}/vote")
def vote_review(review_id: int, vote_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Vote on review helpfulness"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    is_helpful = vote_data.get("is_helpful", True)
    
    # Check existing vote
    existing_vote = db.query(ReviewVote).filter(
        ReviewVote.review_id == review_id, 
        ReviewVote.user_id == current_user.id
    ).first()
    
    if existing_vote:
        # Update existing vote
        if existing_vote.is_helpful != is_helpful:
            existing_vote.is_helpful = is_helpful
            # Update helpful count
            if is_helpful:
                review.helpful_count += 2  # +1 for new helpful, +1 for removing unhelpful
            else:
                review.helpful_count -= 2  # -1 for removing helpful, -1 for new unhelpful
    else:
        # Create new vote
        vote = ReviewVote(review_id=review_id, user_id=current_user.id, is_helpful=is_helpful)
        db.add(vote)
        if is_helpful:
            review.helpful_count += 1
        else:
            review.helpful_count -= 1
    
    db.commit()
    return {"message": "Vote recorded", "helpful_count": review.helpful_count}

@app.get("/api/reviews/{review_id}/votes")
def get_review_votes(review_id: int, db: Session = Depends(get_db)):
    """Get vote statistics for a review"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    helpful_votes = db.query(ReviewVote).filter(
        ReviewVote.review_id == review_id,
        ReviewVote.is_helpful == True
    ).count()
    
    unhelpful_votes = db.query(ReviewVote).filter(
        ReviewVote.review_id == review_id,
        ReviewVote.is_helpful == False
    ).count()
    
    return {
        "helpful_votes": helpful_votes,
        "unhelpful_votes": unhelpful_votes,
        "total_votes": helpful_votes + unhelpful_votes,
        "helpful_percentage": (helpful_votes / (helpful_votes + unhelpful_votes) * 100) if (helpful_votes + unhelpful_votes) > 0 else 0
    }

@app.get("/api/stats/advanced")
def get_advanced_analytics(db: Session = Depends(get_db)):
    """Advanced analytics dashboard with trends and insights"""
    # Basic stats
    total_tools = db.query(Tool).count()
    total_users = db.query(User).count()
    total_reviews = db.query(Review).count()
    
    # Category breakdown with percentages
    categories = db.query(Tool.category, func.count(Tool.id)).group_by(Tool.category).all()
    category_stats = {category: {"count": count, "percentage": round(count/total_tools*100, 1) if total_tools > 0 else 0} for category, count in categories}
    
    # Top tools by stars
    top_tools = db.query(Tool).order_by(Tool.github_stars.desc()).limit(5).all()
    
    # Review statistics
    avg_rating = db.query(func.avg(Review.rating)).scalar() or 0
    review_distribution = db.query(Review.rating, func.count(Review.id)).group_by(Review.rating).all()
    
    # User engagement metrics
    active_reviewers = db.query(func.count(func.distinct(Review.user_id))).scalar() or 0
    avg_reviews_per_tool = total_reviews / total_tools if total_tools > 0 else 0
    
    # Growth trends (mock data for demo)
    growth_trends = {
        "tools_added_last_30_days": 6,
        "users_joined_last_30_days": 25,
        "reviews_last_30_days": 15,
        "monthly_growth_rate": 12.5
    }
    
    return {
        "overview": {
            "total_tools": total_tools,
            "total_users": total_users,
            "total_reviews": total_reviews,
            "average_rating": round(avg_rating, 2),
            "active_reviewers": active_reviewers,
            "avg_reviews_per_tool": round(avg_reviews_per_tool, 2)
        },
        "categories": category_stats,
        "top_tools": [{"name": t.name, "stars": t.github_stars, "category": t.category} for t in top_tools],
        "review_distribution": {str(rating): count for rating, count in review_distribution},
        "growth_trends": growth_trends,
        "insights": [
            f"Most popular category: {max(category_stats.items(), key=lambda x: x[1]['count'])[0]}" if category_stats else "No tools yet - add your first tool!",
            f"Average tool rating: {round(avg_rating, 1)}/5.0",
            f"User engagement: {round(active_reviewers/total_users*100, 1)}% of users have written reviews" if total_users > 0 else "New platform - building user base"
        ]
    }

@app.post("/api/ai/natural-query")
async def natural_language_query(query_data: dict, db: Session = Depends(get_db)):
    """Natural language query interface for tool discovery"""
    query = query_data.get("query", "").lower()
    
    # Simple NLP-like processing for demo
    tools = db.query(Tool).all()
    results = []
    
    # Keyword matching with scoring
    keywords = {
        "monitoring": ["monitoring", "observability", "metrics", "alerting"],
        "container": ["container", "docker", "kubernetes", "orchestration"],
        "ci/cd": ["ci", "cd", "pipeline", "deployment", "build"],
        "infrastructure": ["infrastructure", "terraform", "cloud", "provisioning"]
    }
    
    # Score tools based on query relevance
    for tool in tools:
        score = 0
        tool_text = f"{tool.name} {tool.description} {tool.category}".lower()
        
        # Direct keyword matches
        for word in query.split():
            if word in tool_text:
                score += 2
        
        # Category keyword matches
        for category, category_keywords in keywords.items():
            if any(keyword in query for keyword in category_keywords):
                if tool.category.lower() == category:
                    score += 3
                elif any(keyword in tool_text for keyword in category_keywords):
                    score += 1
        
        if score > 0:
            results.append({
                "tool": {
                    "id": tool.id,
                    "name": tool.name,
                    "description": tool.description[:200] + "...",
                    "category": tool.category,
                    "stars": tool.github_stars
                },
                "relevance_score": score,
                "match_reason": f"Matches your query about {tool.category.lower()} tools"
            })
    
    # Sort by relevance score
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "query": query_data.get("query"),
        "results": results[:10],  # Top 10 results
        "total_matches": len(results),
        "suggestions": [
            "Try: 'monitoring tools for Kubernetes'",
            "Try: 'CI/CD pipeline tools'",
            "Try: 'container orchestration platforms'"
        ]
    }

@app.post("/api/tools/compatibility-check")
def check_tool_compatibility(compatibility_data: dict, db: Session = Depends(get_db)):
    """Check compatibility between tools"""
    tool_ids = compatibility_data.get("tool_ids", [])
    
    if len(tool_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 tools required for compatibility check")
    
    tools = db.query(Tool).filter(Tool.id.in_(tool_ids)).all()
    
    # Compatibility matrix (simplified for demo)
    compatibility_rules = {
        ("Container", "Container"): {"compatible": True, "reason": "Container tools often work together in orchestration"},
        ("Container", "Monitoring"): {"compatible": True, "reason": "Monitoring is essential for containerized applications"},
        ("CI/CD", "Container"): {"compatible": True, "reason": "CI/CD pipelines commonly deploy to containers"},
        ("Infrastructure", "Container"): {"compatible": True, "reason": "Infrastructure tools provision container platforms"},
        ("Monitoring", "Infrastructure"): {"compatible": True, "reason": "Infrastructure monitoring is a common use case"}
    }
    
    results = []
    for i, tool1 in enumerate(tools):
        for tool2 in tools[i+1:]:
            key1 = (tool1.category, tool2.category)
            key2 = (tool2.category, tool1.category)
            
            compatibility = compatibility_rules.get(key1) or compatibility_rules.get(key2) or {
                "compatible": "unknown",
                "reason": "Compatibility depends on specific use case and implementation"
            }
            
            results.append({
                "tool1": {"name": tool1.name, "category": tool1.category},
                "tool2": {"name": tool2.name, "category": tool2.category},
                "compatibility": compatibility["compatible"],
                "reason": compatibility["reason"],
                "integration_tips": f"Consider using {tool1.name} and {tool2.name} together for {tool1.category.lower()}-{tool2.category.lower()} workflows"
            })
    
    return {
        "compatibility_matrix": results,
        "overall_compatibility": "high" if all(r["compatibility"] == True for r in results) else "moderate",
        "recommendations": [
            "These tools can work together effectively",
            "Consider integration patterns and data flow",
            "Check official documentation for specific integration guides"
        ]
    }

@app.get("/api/users/{user_id}/badges")
def get_user_badges(user_id: int, db: Session = Depends(get_db)):
    """Get user badges and reputation system"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate user stats
    user_reviews = db.query(Review).filter(Review.user_id == user_id).all()
    total_reviews = len(user_reviews)
    avg_rating_given = sum(r.rating for r in user_reviews) / total_reviews if total_reviews > 0 else 0
    helpful_votes_received = sum(r.helpful_count for r in user_reviews)
    
    # Badge system
    badges = []
    reputation_score = 0
    
    # Review badges
    if total_reviews >= 1:
        badges.append({"name": "First Reviewer", "description": "Wrote your first review", "icon": "⭐"})
        reputation_score += 10
    if total_reviews >= 5:
        badges.append({"name": "Active Reviewer", "description": "Wrote 5+ reviews", "icon": "📝"})
        reputation_score += 25
    if total_reviews >= 10:
        badges.append({"name": "Review Expert", "description": "Wrote 10+ reviews", "icon": "🏆"})
        reputation_score += 50
    
    # Helpfulness badges
    if helpful_votes_received >= 10:
        badges.append({"name": "Helpful Contributor", "description": "Received 10+ helpful votes", "icon": "👍"})
        reputation_score += 30
    if helpful_votes_received >= 25:
        badges.append({"name": "Community Hero", "description": "Received 25+ helpful votes", "icon": "🦸"})
        reputation_score += 75
    
    # Quality badges
    if avg_rating_given >= 4.0 and total_reviews >= 3:
        badges.append({"name": "Quality Advocate", "description": "Consistently rates quality tools highly", "icon": "💎"})
        reputation_score += 20
    
    # Determine user level
    if reputation_score >= 100:
        level = "Expert"
        level_icon = "🥇"
    elif reputation_score >= 50:
        level = "Advanced"
        level_icon = "🥈"
    elif reputation_score >= 20:
        level = "Intermediate"
        level_icon = "🥉"
    else:
        level = "Beginner"
        level_icon = "🌱"
    
    return {
        "user": {"username": user.username, "id": user.id},
        "reputation_score": reputation_score,
        "level": level,
        "level_icon": level_icon,
        "badges": badges,
        "stats": {
            "total_reviews": total_reviews,
            "avg_rating_given": round(avg_rating_given, 1),
            "helpful_votes_received": helpful_votes_received,
            "account_age_days": (datetime.utcnow() - user.created_at).days
        },
        "next_badge": {
            "name": "Review Master",
            "requirement": "Write 20 reviews",
            "progress": f"{total_reviews}/20"
        } if total_reviews < 20 else None
    }

@app.get("/api/stats")
def get_platform_stats(db: Session = Depends(get_db)):
    """Get platform statistics"""
    total_tools = db.query(Tool).count()
    total_users = db.query(User).count()
    total_reviews = db.query(Review).count()
    
    # Get category breakdown
    categories = db.query(Tool.category, func.count(Tool.id)).group_by(Tool.category).all()
    category_stats = {category: count for category, count in categories}
    
    return {
        "total_tools": total_tools,
        "total_users": total_users,
        "total_reviews": total_reviews,
        "categories": category_stats,
        "top_categories": sorted(category_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    }

@app.post("/api/ai/enhanced-compare")
async def enhanced_compare_tools(request: dict):
    """Real-time AI-powered tool comparison for any tools"""
    try:
        tool1 = request.get('tool1', '').strip()
        tool2 = request.get('tool2', '').strip()
        
        if not tool1 or not tool2:
            raise HTTPException(status_code=400, detail="Both tool names are required")
        
        # Try AI first, fallback to knowledge base
        try:
            return await generate_enhanced_ai_comparison(tool1, tool2)
        except Exception as ai_error:
            logger.warning(f"AI comparison failed: {ai_error}, using knowledge base")
            return generate_detailed_comparison(tool1, tool2)
            
    except Exception as e:
        logger.error(f"Failed to generate comparison: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate comparison")

async def generate_enhanced_ai_comparison(tool1: str, tool2: str):
    """Generate comparison using AI with structured prompt"""
    
    # Configure Gemini AI
    api_key = os.getenv('GEMINI_API_KEY', '')
    if not api_key or api_key == 'your-gemini-api-key':
        raise Exception("AI API key not configured")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-3-flash-preview')
    
    prompt = f"""Compare {tool1} vs {tool2} as a DevOps consultant. Provide ONLY a JSON response with this exact structure (no markdown, no code blocks):

{{
  "tool1": "{tool1}",
  "tool2": "{tool2}",
  "detailed_analysis": {{
    "overview": "2-3 sentence executive summary with market share percentages if known",
    "technical_comparison": {{
      "architecture": "Tool1: [architecture details]. Tool2: [architecture details]",
      "performance": "Tool1: [specific metrics like startup time, throughput]. Tool2: [specific metrics]",
      "scalability": "Tool1: [scaling capabilities with numbers]. Tool2: [scaling capabilities with numbers]",
      "security": "Tool1: [compliance certs like SOC2, ISO]. Tool2: [compliance certs]"
    }},
    "business_analysis": {{
      "cost_analysis": "Tool1: [pricing with $ amounts]. Tool2: [pricing with $ amounts]. ROI Analysis: [comparison]",
      "learning_curve": "Tool1: [time to proficiency, resources]. Tool2: [time to proficiency, resources]",
      "community_support": "Tool1: Market share X%, [integrations count]. Tool2: Market share Y%, [integrations count]",
      "enterprise_readiness": "Tool1: [enterprise features]. Tool2: [enterprise features]"
    }},
    "use_case_scenarios": {{
      "startup": "Startups (<50 employees): Recommend [tool] because [reason]. Migration: [effort]",
      "enterprise": "Enterprise (500+ employees): Tool1 for [use case]. Tool2 for [use case]",
      "specific_industries": "Regulated Industries: [tool] - [compliance]. Tech/Startups: [tool] - [reason]"
    }},
    "pros_cons": {{
      "tool1_pros": ["Quantitative strength 1", "Quantitative strength 2", "Quantitative strength 3", "Quantitative strength 4", "Quantitative strength 5"],
      "tool1_cons": ["Specific limitation 1", "Specific limitation 2", "Specific limitation 3", "Specific limitation 4"],
      "tool2_pros": ["Quantitative strength 1", "Quantitative strength 2", "Quantitative strength 3", "Quantitative strength 4", "Quantitative strength 5"],
      "tool2_cons": ["Specific limitation 1", "Specific limitation 2", "Specific limitation 3", "Specific limitation 4"]
    }},
    "decision_matrix": [
      {{"criteria": "Ease of Use", "tool1_score": 7, "tool2_score": 8, "reasoning": "Brief reason"}},
      {{"criteria": "Performance", "tool1_score": 8, "tool2_score": 7, "reasoning": "Brief reason"}},
      {{"criteria": "Enterprise Features", "tool1_score": 7, "tool2_score": 9, "reasoning": "Brief reason"}},
      {{"criteria": "Community Support", "tool1_score": 9, "tool2_score": 7, "reasoning": "Brief reason"}},
      {{"criteria": "Cost Effectiveness", "tool1_score": 8, "tool2_score": 6, "reasoning": "Brief reason"}},
      {{"criteria": "Security", "tool1_score": 8, "tool2_score": 9, "reasoning": "Brief reason"}},
      {{"criteria": "Scalability", "tool1_score": 9, "tool2_score": 8, "reasoning": "Brief reason"}},
      {{"criteria": "Integration Ecosystem", "tool1_score": 8, "tool2_score": 9, "reasoning": "Brief reason"}}
    ],
    "final_recommendation": "Overall Score: Tool1 (X/80) vs Tool2 (Y/80). Choose Tool1 if: [specific criteria]. Choose Tool2 if: [specific criteria]. Migration Path: [details]. Sources: [list sources]"
  }},
  "metadata": {{
    "data_sources": ["Source 1", "Source 2", "Source 3"],
    "last_updated": "2024-Q4",
    "confidence_level": "High"
  }}
}}

Use real data: GitHub stars, pricing, compliance certs (SOC2, ISO27001), market share %, performance metrics. Be specific with numbers."""

    response = model.generate_content(prompt)
    response_text = response.text.strip()
    
    # Clean response
    if '```json' in response_text:
        response_text = response_text.split('```json')[1].split('```')[0].strip()
    elif '```' in response_text:
        response_text = response_text.split('```')[1].split('```')[0].strip()
    
    return json.loads(response_text)

def generate_detailed_comparison(tool1: str, tool2: str):
    """Generate production-grade comparison with quantitative data"""
    
    t1_data = get_tool_data(tool1)
    t2_data = get_tool_data(tool2)
    roi = calculate_roi(t1_data['cost'], t2_data['cost'])
    
    # Calculate weighted scores based on quantitative metrics
    def calculate_score(tool_data, criterion):
        scores = {
            "Ease of Use": 8 if "weeks" in tool_data['learning_curve'].lower() else 6,
            "Performance": 9 if "faster" in tool_data['performance'].lower() or "low" in tool_data['performance'].lower() else 7,
            "Enterprise Features": 9 if "SOC 2" in tool_data['compliance'] or "ISO" in tool_data['compliance'] else 6,
            "Community Support": 9 if tool_data['market_share'] != "Market share data not available" and float(tool_data['market_share'].rstrip('%')) > 50 else 7,
            "Cost Effectiveness": 9 if "free" in tool_data['cost'].lower() or "$0" in tool_data['cost'] else 6,
            "Security": 9 if "SOC 2" in tool_data['compliance'] else 7,
            "Scalability": 8 if "scale" in tool_data['benchmarks'].lower() else 7,
            "Integration Ecosystem": 9 if "1000+" in tool_data['integrations'] or "200+" in tool_data['integrations'] else 7
        }
        return scores.get(criterion, 7)
    
    criteria_list = ["Ease of Use", "Performance", "Enterprise Features", "Community Support", "Cost Effectiveness", "Security", "Scalability", "Integration Ecosystem"]
    
    decision_matrix = []
    for criterion in criteria_list:
        t1_score = calculate_score(t1_data, criterion)
        t2_score = calculate_score(t2_data, criterion)
        winner = tool1 if t1_score > t2_score else tool2 if t2_score > t1_score else "Tie"
        decision_matrix.append({
            "criteria": criterion,
            "tool1_score": t1_score,
            "tool2_score": t2_score,
            "reasoning": f"{winner} leads based on quantitative metrics"
        })
    
    # Calculate overall winner
    t1_total = sum(item['tool1_score'] for item in decision_matrix)
    t2_total = sum(item['tool2_score'] for item in decision_matrix)
    
    return {
        "tool1": tool1,
        "tool2": tool2,
        "detailed_analysis": {
            "overview": f"{tool1} ({t1_data['category']}) vs {tool2} ({t2_data['category']}): {tool1} holds {t1_data.get('market_share', 'N/A')} market share while {tool2} has {t2_data.get('market_share', 'N/A')}. Both serve similar use cases but with different architectural approaches and cost structures.",
            "technical_comparison": {
                "architecture": f"**{tool1}**: {t1_data['architecture']}\n\n**{tool2}**: {t2_data['architecture']}",
                "performance": f"**{tool1}**: {t1_data['performance']}\n\n**{tool2}**: {t2_data['performance']}",
                "scalability": f"**{tool1}**: {t1_data['benchmarks']}\n\n**{tool2}**: {t2_data['benchmarks']}",
                "security": f"**{tool1}**: {t1_data['compliance']}\n\n**{tool2}**: {t2_data['compliance']}"
            },
            "business_analysis": {
                "cost_analysis": f"**{tool1}**: {t1_data['cost']}\n\n**{tool2}**: {t2_data['cost']}\n\n**ROI Analysis**: {roi['tool1_monthly']} vs {roi['tool2_monthly']}. {roi['annual_difference']}. {roi['note']}",
                "learning_curve": f"**{tool1}**: {t1_data['learning_curve']}\n\n**{tool2}**: {t2_data['learning_curve']}",
                "community_support": f"**{tool1}**: Market share {t1_data.get('market_share', 'N/A')}, {t1_data['integrations']}\n\n**{tool2}**: Market share {t2_data.get('market_share', 'N/A')}, {t2_data['integrations']}",
                "enterprise_readiness": f"**{tool1}**: {t1_data['enterprise_features']}\n\n**{tool2}**: {t2_data['enterprise_features']}"
            },
            "use_case_scenarios": {
                "startup": f"**Startups (<50 employees)**: Choose {tool2} if cost-sensitive. Choose {tool1} if you need proven stability. Migration effort: {t2_data['migration_effort']}",
                "enterprise": f"**Enterprise (500+ employees)**: {tool1} recommended for: {', '.join(t1_data['strengths'][:2])}. {tool2} recommended for: {', '.join(t2_data['strengths'][:2])}.",
                "specific_industries": f"**Regulated Industries**: {tool1} - {t1_data['compliance']}. **Tech/Startups**: {tool2} offers {t2_data['strengths'][0]}. **Migration**: {t1_data['migration_effort']} for {tool1}, {t2_data['migration_effort']} for {tool2}"
            },
            "pros_cons": {
                "tool1_pros": t1_data['strengths'],
                "tool1_cons": t1_data['weaknesses'],
                "tool2_pros": t2_data['strengths'],
                "tool2_cons": t2_data['weaknesses']
            },
            "decision_matrix": decision_matrix,
            "final_recommendation": f"**Overall Score**: {tool1} ({t1_total}/80) vs {tool2} ({t2_total}/80)\n\n**Choose {tool1} if**: You need {t1_data['strengths'][0].lower()}, have budget for {t1_data['cost'].split('|')[0] if '|' in t1_data['cost'] else t1_data['cost'][:50]}, and require {t1_data['compliance'].split(',')[0] if ',' in t1_data['compliance'] else 'enterprise compliance'}.\n\n**Choose {tool2} if**: You prioritize {t2_data['strengths'][0].lower()}, want {t2_data['cost'].split('|')[0] if '|' in t2_data['cost'] else t2_data['cost'][:50]}, and can accept {t2_data['migration_effort'].lower()}.\n\n**Migration Path**: {t2_data['migration_effort']}. Estimated timeline: 2-8 weeks.\n\n**Sources**: {', '.join(t1_data.get('sources', ['Vendor documentation']))}"
        },
        "metadata": {
            "data_sources": list(set(t1_data.get('sources', []) + t2_data.get('sources', []))),
            "last_updated": "2024-Q4",
            "confidence_level": "High" if t1_data.get('sources') and t2_data.get('sources') else "Medium"
        }
    }

@app.post("/api/ai/search")
async def ai_search_tools(request: dict, db: Session = Depends(get_db)):
    """Enhanced AI-powered tool search using comprehensive data"""
    query = request.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    try:
        # Get all tools with comprehensive data
        tools = db.query(Tool).all()
        
        # Create enhanced search context with all fetched data
        tools_context = []
        for tool in tools:
            # Extract key information for AI search
            context = {
                "name": tool.name,
                "category": tool.category,
                "description": tool.description[:1000],  # Limit for AI context
                "license": tool.license,
                "pricing": tool.pricing_model,
                "stars": tool.github_stars,
                "forks": tool.github_forks,
                "ai_summary": tool.ai_summary
            }
            
            # Extract features from enhanced description
            features = []
            if "**Key Features:**" in tool.description:
                features_section = tool.description.split("**Key Features:**")[1].split("**")[0]
                features = [f.strip() for f in features_section.split("•") if f.strip()][:5]
            
            context["features"] = features
            tools_context.append(context)
        
        # Use AI to analyze and recommend tools
        if GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-api-key":
            model = genai.GenerativeModel('models/gemini-3-flash-preview')
            
            prompt = f"""
You are an expert DevOps consultant. A user is asking: "{query}"

Based on this query, analyze the following tools and provide recommendations:

{json.dumps(tools_context, indent=2)}

Provide a JSON response with:
{{
    "recommended_tools": [
        {{
            "name": "Tool Name",
            "relevance_score": 95,
            "why_recommended": "Specific reason why this tool matches the query",
            "use_case": "How to use this tool for the user's needs"
        }}
    ],
    "search_summary": "Brief explanation of the search results",
    "alternative_suggestions": ["suggestion 1", "suggestion 2"]
}}

Focus on practical recommendations. Return only valid JSON.
"""
            
            response = model.generate_content(prompt)
            
            try:
                # Parse AI response
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                ai_results = json.loads(response_text)
                
                # Enhance results with actual tool data
                enhanced_tools = []
                for rec_tool in ai_results.get("recommended_tools", []):
                    matching_tool = next((t for t in tools if t.name.lower() == rec_tool["name"].lower()), None)
                    if matching_tool:
                        enhanced_tool = {
                            **rec_tool,
                            "id": matching_tool.id,
                            "slug": matching_tool.slug,
                            "category": matching_tool.category,
                            "github_stars": matching_tool.github_stars,
                            "license": matching_tool.license,
                            "pricing_model": matching_tool.pricing_model,
                            "homepage_url": matching_tool.homepage_url
                        }
                        enhanced_tools.append(enhanced_tool)
                
                ai_results["recommended_tools"] = enhanced_tools
                return ai_results
                
            except json.JSONDecodeError:
                pass
        
        # Fallback: Enhanced keyword search
        query_lower = query.lower()
        scored_tools = []
        
        for tool in tools:
            score = 0
            reasons = []
            
            if query_lower in tool.name.lower():
                score += 50
                reasons.append("Name matches")
            if query_lower in tool.category.lower():
                score += 30
                reasons.append("Category matches")
            if query_lower in tool.description.lower():
                score += 20
                reasons.append("Description matches")
            if "**Key Features:**" in tool.description:
                features_section = tool.description.split("**Key Features:**")[1].split("**")[0]
                if query_lower in features_section.lower():
                    score += 25
                    reasons.append("Features match")
            
            if score > 0:
                scored_tools.append({
                    "name": tool.name,
                    "id": tool.id,
                    "slug": tool.slug,
                    "relevance_score": min(score, 100),
                    "why_recommended": "; ".join(reasons),
                    "use_case": f"Use for {tool.category.lower()} needs",
                    "category": tool.category,
                    "github_stars": tool.github_stars,
                    "license": tool.license,
                    "pricing_model": tool.pricing_model,
                    "homepage_url": tool.homepage_url
                })
        
        scored_tools.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return {
            "recommended_tools": scored_tools[:5],
            "search_summary": f"Found {len(scored_tools)} tools matching '{query}'",
            "alternative_suggestions": ["Try specific keywords", "Search by category"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search failed")

@app.get("/api/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get comprehensive analytics overview"""
    try:
        # Get basic counts
        total_tools = db.query(Tool).count()
        
        # Category distribution
        category_stats = db.query(Tool.category, func.count(Tool.id)).group_by(Tool.category).all()
        
        # Pricing model distribution
        pricing_stats = db.query(Tool.pricing_model, func.count(Tool.id)).group_by(Tool.pricing_model).all()
        
        # License distribution
        license_stats = db.query(Tool.license, func.count(Tool.id)).group_by(Tool.license).all()
        
        # Top tools by stars
        top_tools = db.query(Tool).order_by(Tool.github_stars.desc()).limit(10).all()
        
        # GitHub statistics
        total_stars = db.query(func.sum(Tool.github_stars)).scalar() or 0
        total_forks = db.query(func.sum(Tool.github_forks)).scalar() or 0
        avg_stars = db.query(func.avg(Tool.github_stars)).scalar() or 0
        
        # Growth trends (mock data for now - can be enhanced with real tracking)
        growth_data = [
            {"month": "Jan", "tools": 5, "stars": 50000},
            {"month": "Feb", "tools": 6, "stars": 75000},
            {"month": "Mar", "tools": 8, "stars": 120000},
            {"month": "Apr", "tools": 10, "stars": 180000},
            {"month": "May", "tools": 10, "stars": total_stars}
        ]
        
        # Build insights safely (avoid max() on empty sequences)
        insights = []
        if category_stats:
            top_cat = max(category_stats, key=lambda x: x[1])
            insights.append(f"Most popular category: {top_cat[0]} ({top_cat[1]} tools)")
        insights.append(f"Average GitHub stars per tool: {int(avg_stars):,}")
        licenses_with_name = [l for l in license_stats if l[0]]
        if licenses_with_name:
            top_license = max(licenses_with_name, key=lambda x: x[1])
            insights.append(f"Most common license: {top_license[0]}")
        insights.append(f"Total community engagement: {int(total_stars + total_forks):,} stars + forks")

        return {
            "overview": {
                "total_tools": total_tools,
                "total_stars": int(total_stars),
                "total_forks": int(total_forks),
                "avg_stars": int(avg_stars),
                "categories": len(category_stats),
                "licenses": len(licenses_with_name)
            },
            "category_distribution": [
                {"name": cat, "count": count, "percentage": round((count / total_tools) * 100, 1) if total_tools else 0}
                for cat, count in category_stats
            ],
            "pricing_distribution": [
                {"name": pricing.title() if pricing else "Unknown", "count": count, "percentage": round((count / total_tools) * 100, 1) if total_tools else 0}
                for pricing, count in pricing_stats
            ],
            "license_distribution": [
                {"name": lic or "Unknown", "count": count, "percentage": round((count / total_tools) * 100, 1) if total_tools else 0}
                for lic, count in license_stats if count > 0
            ][:10],
            "top_tools": [
                {
                    "name": tool.name,
                    "category": tool.category,
                    "stars": tool.github_stars,
                    "forks": tool.github_forks,
                    "license": tool.license,
                    "pricing": tool.pricing_model
                }
                for tool in top_tools
            ],
            "growth_trends": growth_data,
            "insights": insights
        }
    except Exception as e:
        logger.error(f"Analytics error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load analytics")

@app.get("/api/analytics/tools/{tool_id}")
async def get_tool_analytics(tool_id: int, db: Session = Depends(get_db)):
    """Get analytics for a specific tool"""
    try:
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        # Get category peers for comparison
        category_peers = db.query(Tool).filter(
            Tool.category == tool.category,
            Tool.id != tool.id
        ).order_by(Tool.github_stars.desc()).limit(5).all()
        
        # Calculate rankings
        category_rank = db.query(Tool).filter(
            Tool.category == tool.category,
            Tool.github_stars > tool.github_stars
        ).count() + 1
        
        overall_rank = db.query(Tool).filter(
            Tool.github_stars > tool.github_stars
        ).count() + 1
        
        return {
            "tool": {
                "name": tool.name,
                "category": tool.category,
                "stars": tool.github_stars,
                "forks": tool.github_forks,
                "license": tool.license,
                "pricing": tool.pricing_model
            },
            "rankings": {
                "category_rank": category_rank,
                "overall_rank": overall_rank,
                "category_total": db.query(Tool).filter(Tool.category == tool.category).count()
            },
            "category_peers": [
                {
                    "name": peer.name,
                    "stars": peer.github_stars,
                    "forks": peer.github_forks
                }
                for peer in category_peers
            ],
            "metrics": {
                "popularity_score": min(100, (tool.github_stars / 1000) * 10),
                "community_engagement": tool.github_stars + tool.github_forks,
                "fork_ratio": round((tool.github_forks / max(tool.github_stars, 1)) * 100, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to load tool analytics")

@app.post("/api/admin/enhance-tools")
async def enhance_tools_endpoint(current_user: User = Depends(get_admin_user)):
    """Enhance all tools with GitHub README data (requires auth)"""
    try:
        from enhance_tools import ToolEnhancer
        enhancer = ToolEnhancer()
        enhancer.enhance_all_tools()
        return {"message": "Tools enhanced successfully", "status": "success"}
    except Exception as e:
        logger.error(f"Enhancement failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Enhancement failed")

@app.post("/api/admin/enhance-tool/{tool_id}")
async def enhance_single_tool(tool_id: int, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Enhance a single tool with GitHub README data"""
    try:
        from enhance_tools import ToolEnhancer
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        enhancer = ToolEnhancer()
        github_info = enhancer.extract_github_info(tool.github_url)
        
        if github_info:
            readme_content = enhancer.fetch_github_readme(github_info['owner'], github_info['repo'])
            github_stats = enhancer.fetch_github_stats(github_info['owner'], github_info['repo'])
            
            if readme_content:
                readme_info = enhancer.parse_readme_content(readme_content)
                enhanced_description = enhancer.enhance_tool_description(tool, readme_info, github_stats)
                tool.description = enhanced_description
                
                # Update stats
                if github_stats.get('stars'):
                    tool.github_stars = github_stats['stars']
                if github_stats.get('forks'):
                    tool.github_forks = github_stats['forks']
                
                db.commit()
                return {"message": f"Tool {tool.name} enhanced successfully", "status": "success"}
        
        raise HTTPException(status_code=400, detail="Could not enhance tool")
    except Exception as e:
        logger.error(f"Enhancement failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Enhancement failed")

@app.post("/api/admin/ingest-tools")
async def trigger_tool_ingestion(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Trigger ingestion of 100+ DevOps tools from GitHub API (admin only)"""
    try:
        from tool_ingestion import tool_ingestion_service
        result = await tool_ingestion_service.ingest_all(db)
        return {
            "message": f"Ingested {result['count']} tools ({result['created']} new, {result['updated']} updated)",
            "count": result["count"],
            "created": result["created"],
            "updated": result["updated"],
            "errors": result["errors"][:10],  # Limit error list size
        }
    except Exception as e:
        logger.error(f"Tool ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Tool ingestion failed")

@app.get("/api/tools/{tool_id}/health")
async def get_tool_health(tool_id: int, db: Session = Depends(get_db)):
    """Get health score breakdown for a specific tool"""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    if tool.health_data:
        try:
            return json.loads(tool.health_data)
        except json.JSONDecodeError:
            pass

    # Calculate on-the-fly if no cached data
    if tool.github_url:
        from health_scoring import health_scoring_service
        result = await health_scoring_service.calculate_health_score(
            tool.github_url, tool.github_stars or 0
        )
        # Cache the result
        tool.health_score = result.get("score", 0)
        tool.health_data = json.dumps(result)
        tool.last_health_check = datetime.utcnow()
        db.commit()
        return result

    return {"score": 0, "grade": "F", "breakdown": {}, "error": "No GitHub URL"}

@app.post("/api/admin/recalculate-health")
async def recalculate_health_scores(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Recalculate health scores for all tools (admin only)"""
    try:
        from health_scoring import health_scoring_service
        result = await health_scoring_service.score_all_tools(db)
        return {
            "message": f"Scored {result['scored']} tools",
            "scored": result["scored"],
            "errors": result["errors"][:10],
            "tools": result["tools"],
        }
    except Exception as e:
        logger.error(f"Health scoring failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Health scoring failed")

# Blog endpoints
@app.get("/api/blogs")
async def get_blogs(db: Session = Depends(get_db)):
    """Get all blogs"""
    blogs = db.query(Blog).order_by(Blog.created_at.desc()).all()
    return blogs

@app.post("/api/blogs")
async def create_blog(blog_data: BlogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new blog (requires authentication)"""
    blog = Blog(title=blog_data.title, content=blog_data.content, author=blog_data.author)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog

# ===== USAGE TRACKING ENDPOINTS =====

@app.get("/api/usage/me")
async def get_my_usage(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's usage summary for today"""
    from usage_tracking import get_usage_summary
    return get_usage_summary(db, current_user)

@app.get("/api/ai/compare/export")
async def export_comparison(
    tool_ids: str,
    format: str = "markdown",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export a comparison report (pro/enterprise only)"""
    from usage_tracking import check_and_increment_usage
    usage = check_and_increment_usage(db, current_user, "exports")
    if not usage["allowed"]:
        raise HTTPException(
            status_code=402,
            detail={
                "message": "Export requires a Pro or Enterprise plan",
                "upgrade_url": "/pricing",
                "plan": usage["plan"],
            },
        )

    ids = [int(x.strip()) for x in tool_ids.split(",") if x.strip().isdigit()]
    tools = db.query(Tool).filter(Tool.id.in_(ids)).all()
    if len(tools) < 2:
        raise HTTPException(status_code=400, detail="At least 2 tools required")

    if format == "json":
        return {
            "tools": [
                {
                    "name": t.name,
                    "category": t.category,
                    "stars": t.github_stars,
                    "license": t.license,
                    "pricing": t.pricing_model,
                    "health_score": t.health_score,
                    "description": t.description,
                }
                for t in tools
            ],
            "exported_at": datetime.utcnow().isoformat(),
        }

    # Default: markdown
    lines = [f"# Tool Comparison Report\n", f"*Generated {datetime.utcnow().strftime('%Y-%m-%d')}*\n"]
    for t in tools:
        lines.append(f"## {t.name}")
        lines.append(f"- **Category**: {t.category}")
        lines.append(f"- **Stars**: {t.github_stars:,}")
        lines.append(f"- **License**: {t.license or 'N/A'}")
        lines.append(f"- **Pricing**: {t.pricing_model}")
        lines.append(f"- **Health Score**: {t.health_score or 'N/A'}/100")
        lines.append(f"- **Description**: {t.description[:300]}")
        lines.append("")
    return Response(content="\n".join(lines), media_type="text/markdown")

# ===== NEWSLETTER / EMAIL ENDPOINTS =====

@app.post("/api/newsletter/subscribe")
async def subscribe_newsletter(data: dict, db: Session = Depends(get_db)):
    """Subscribe to newsletter (public endpoint)"""
    email = data.get("email", "").strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email required")

    existing = db.query(EmailSubscriber).filter(EmailSubscriber.email == email).first()
    if existing:
        if not existing.is_active:
            existing.is_active = True
            db.commit()
        return {"message": "Already subscribed", "status": "ok"}

    subscriber = EmailSubscriber(
        email=email,
        name=data.get("name", ""),
        source=data.get("source", "homepage"),
    )
    db.add(subscriber)
    db.commit()
    return {"message": "Subscribed successfully", "status": "ok"}

@app.get("/api/admin/subscribers")
async def list_subscribers(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """List all email subscribers (admin only)"""
    subs = db.query(EmailSubscriber).filter(EmailSubscriber.is_active == True).order_by(EmailSubscriber.subscribed_at.desc()).all()
    return [{"id": s.id, "email": s.email, "name": s.name, "source": s.source, "subscribed_at": s.subscribed_at.isoformat()} for s in subs]

@app.get("/api/admin/subscribers/export")
async def export_subscribers(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Export subscribers as CSV (admin only)"""
    subs = db.query(EmailSubscriber).filter(EmailSubscriber.is_active == True).all()
    lines = ["email,name,source,subscribed_at"]
    for s in subs:
        lines.append(f"{s.email},{s.name or ''},{s.source or ''},{s.subscribed_at.isoformat()}")
    return Response(content="\n".join(lines), media_type="text/csv")

# ===== SEO COMPARISON PAGES =====

@app.get("/api/comparisons")
async def list_comparisons(db: Session = Depends(get_db)):
    """List all SEO comparison pages"""
    pages = db.query(ComparisonPage).order_by(ComparisonPage.views.desc()).all()
    return [
        {
            "id": p.id,
            "slug": p.slug,
            "title": p.title,
            "meta_description": p.meta_description,
            "views": p.views,
            "tool_a": p.tool_a.name if p.tool_a else None,
            "tool_b": p.tool_b.name if p.tool_b else None,
        }
        for p in pages
    ]

@app.get("/api/comparisons/{slug}")
async def get_comparison_page(slug: str, db: Session = Depends(get_db)):
    """Get a specific SEO comparison page and increment views"""
    page = db.query(ComparisonPage).filter(ComparisonPage.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Comparison page not found")
    page.views = (page.views or 0) + 1
    db.commit()
    return {
        "id": page.id,
        "slug": page.slug,
        "title": page.title,
        "content": page.content,
        "meta_description": page.meta_description,
        "views": page.views,
        "tool_a": {"id": page.tool_a.id, "name": page.tool_a.name, "slug": page.tool_a.slug} if page.tool_a else None,
        "tool_b": {"id": page.tool_b.id, "name": page.tool_b.name, "slug": page.tool_b.slug} if page.tool_b else None,
        "generated_at": page.generated_at.isoformat() if page.generated_at else None,
    }

@app.post("/api/admin/generate-comparisons")
async def generate_comparison_pages(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Auto-generate top SEO comparison pages (admin only)"""
    TOP_PAIRS = [
        ("Docker", "Podman"), ("Docker", "Kubernetes"), ("Kubernetes", "Nomad"),
        ("Terraform", "Pulumi"), ("Terraform", "Ansible"), ("Terraform", "OpenTofu"),
        ("Jenkins", "GitHub Actions"), ("Jenkins", "GitLab CI/CD"), ("GitHub Actions", "GitLab CI/CD"),
        ("ArgoCD", "Flux"), ("ArgoCD", "Spinnaker"), ("Tekton", "GitHub Actions"),
        ("Prometheus", "Grafana"), ("Prometheus", "VictoriaMetrics"), ("Prometheus", "Zabbix"),
        ("Grafana", "Kibana"), ("Loki", "Elasticsearch"), ("Fluentd", "Fluent Bit"),
        ("Istio", "Linkerd"), ("Traefik", "NGINX"), ("Envoy Proxy", "NGINX"),
        ("Ansible", "Chef"), ("Ansible", "Puppet"), ("Ansible", "SaltStack"),
        ("Vault", "cert-manager"), ("Trivy", "Grype"), ("Falco", "Open Policy Agent"),
        ("Helm", "Kustomize"), ("k3s", "MicroK8s"), ("k3s", "Minikube"),
        ("Redis", "etcd"), ("PostgreSQL", "MySQL"), ("PostgreSQL", "CockroachDB"),
        ("MinIO", "Longhorn"), ("Kong", "Traefik"), ("Kong", "APISIX"),
        ("k6", "Locust"), ("k6", "JMeter"), ("Litmus Chaos", "Chaos Mesh"),
        ("Docker Compose", "Kubernetes"), ("Rancher", "Kubernetes"),
        ("OpenFaaS", "Knative"), ("Caddy", "NGINX"), ("HAProxy", "NGINX"),
        ("Consul", "Istio"), ("Cilium", "Istio"), ("CoreDNS", "Consul"),
        ("Apache Kafka", "RabbitMQ"), ("Apache Kafka", "NATS"), ("RabbitMQ", "NATS"),
        ("Velero", "Longhorn"), ("Crossplane", "Terraform"),
    ]

    created = 0
    skipped = 0
    errors = []

    for name_a, name_b in TOP_PAIRS:
        tool_a = db.query(Tool).filter(Tool.name == name_a).first()
        tool_b = db.query(Tool).filter(Tool.name == name_b).first()

        if not tool_a or not tool_b:
            skipped += 1
            continue

        slug = f"{tool_a.slug}-vs-{tool_b.slug}"
        existing = db.query(ComparisonPage).filter(ComparisonPage.slug == slug).first()
        if existing:
            skipped += 1
            continue

        try:
            title = f"{tool_a.name} vs {tool_b.name} (2025): Complete Comparison"
            meta = f"Compare {tool_a.name} and {tool_b.name} - features, performance, pricing, and use cases. Find the best {tool_a.category.lower()} tool for your needs."

            content = _generate_comparison_content(tool_a, tool_b)

            page = ComparisonPage(
                tool_a_id=tool_a.id,
                tool_b_id=tool_b.id,
                slug=slug,
                title=title,
                content=content,
                meta_description=meta,
            )
            db.add(page)
            created += 1
        except Exception as e:
            errors.append(f"{name_a} vs {name_b}: {str(e)}")

    db.commit()
    return {"created": created, "skipped": skipped, "errors": errors[:10]}


def _generate_comparison_content(tool_a, tool_b) -> str:
    """Generate structured comparison content for two tools."""
    return f"""## Overview

**{tool_a.name}** and **{tool_b.name}** are both popular tools in the {tool_a.category} / {tool_b.category} space. This comparison helps you choose the right tool for your DevOps workflow.

### {tool_a.name}
{tool_a.description or 'A widely-used DevOps tool.'}

### {tool_b.name}
{tool_b.description or 'A widely-used DevOps tool.'}

## Quick Comparison

| Feature | {tool_a.name} | {tool_b.name} |
|---------|{'---' * 5}|{'---' * 5}|
| **GitHub Stars** | {tool_a.github_stars:,} | {tool_b.github_stars:,} |
| **License** | {tool_a.license or 'N/A'} | {tool_b.license or 'N/A'} |
| **Pricing** | {tool_a.pricing_model} | {tool_b.pricing_model} |
| **Category** | {tool_a.category} | {tool_b.category} |
| **Health Score** | {tool_a.health_score or 'N/A'}/100 | {tool_b.health_score or 'N/A'}/100 |

## Community & Adoption

{tool_a.name} has **{tool_a.github_stars:,}** GitHub stars and **{tool_a.github_forks:,}** forks, while {tool_b.name} has **{tool_b.github_stars:,}** stars and **{tool_b.github_forks:,}** forks.

## Use Cases

**Choose {tool_a.name} if:**
- You need a mature, well-established solution
- Your team is already familiar with {tool_a.name}'s ecosystem
- You prioritize {tool_a.category.lower()} features

**Choose {tool_b.name} if:**
- You want a {'lightweight' if tool_b.github_stars < tool_a.github_stars else 'feature-rich'} alternative
- You're starting a new project with flexibility
- You prioritize {tool_b.category.lower()} capabilities

## Verdict

Both {tool_a.name} and {tool_b.name} are excellent choices. {tool_a.name} {'has a larger community' if tool_a.github_stars > tool_b.github_stars else 'is gaining traction'}, while {tool_b.name} {'offers a strong alternative' if tool_b.github_stars < tool_a.github_stars else 'leads in popularity'}. Your choice should depend on your specific requirements, team expertise, and infrastructure needs.
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
