from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr
import requests
import json
from datetime import datetime, timedelta
from typing import List, Optional
import jwt
import bcrypt
import os
from contextlib import contextmanager
import asyncio
import aiohttp
import google.generativeai as genai

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cloudengineered.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
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
    avatar_url = Column(String)
    bio = Column(Text)
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
    is_helpful = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)

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
    rating: int
    content: str

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

class Token(BaseModel):
    access_token: str
    token_type: str

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="CloudEngineered API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")

# Configure Gemini AI
if GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-api-key":
    genai.configure(api_key=GEMINI_API_KEY)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

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
        print(f"Error fetching GitHub stats: {e}")
    
    return {"stars": 0, "forks": 0, "last_commit": None}

async def generate_ai_comparison(tools: List[Tool]) -> dict:
    """Generate AI-powered tool comparison using Gemini"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your-gemini-api-key":
        # Fallback to mock comparison
        return generate_mock_comparison(tools)
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
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
        print(f"Gemini API error: {e}")
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

# Routes
@app.get("/")
def read_root():
    return {"message": "CloudEngineered API", "version": "1.0.0"}

@app.post("/api/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
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
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not bcrypt.checkpw(login_data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.id})
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

@app.post("/api/tools", response_model=ToolResponse)
async def create_tool(tool: ToolCreate, db: Session = Depends(get_db)):
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

@app.get("/api/tools/{tool_id}/reviews", response_model=List[ReviewResponse])
def get_tool_reviews(tool_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.tool_id == tool_id).all()
    return reviews

@app.post("/api/tools/{tool_id}/reviews", response_model=ReviewResponse)
def create_review(tool_id: int, review: ReviewCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if tool exists
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Check if user already reviewed this tool
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

@app.get("/api/users/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/api/ai/compare")
async def compare_tools(request: CompareRequest, db: Session = Depends(get_db)):
    """Generate AI-powered tool comparison using Gemini"""
    tools = db.query(Tool).filter(Tool.id.in_(request.tool_ids)).all()
    
    if len(tools) < 2:
        raise HTTPException(status_code=400, detail="At least 2 tools required for comparison")
    
    comparison = await generate_ai_comparison(tools)
    return comparison

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

# Review voting endpoints
@app.post("/api/reviews/{review_id}/vote")
def vote_review(review_id: int, is_helpful: bool, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Vote on review helpfulness"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check existing vote
    existing_vote = db.query(ReviewVote).filter(ReviewVote.review_id == review_id, ReviewVote.user_id == current_user.id).first()
    
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
    return {"message": "Vote recorded"}

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

@app.get("/api/stats")
def get_platform_stats(db: Session = Depends(get_db)):
    """Get platform statistics"""
    total_tools = db.query(Tool).count()
    total_users = db.query(User).count()
    total_reviews = db.query(Review).count()
    
    # Get category breakdown
    categories = db.query(Tool.category, db.func.count(Tool.id)).group_by(Tool.category).all()
    category_stats = {category: count for category, count in categories}
    
    return {
        "total_tools": total_tools,
        "total_users": total_users,
        "total_reviews": total_reviews,
        "categories": category_stats,
        "top_categories": sorted(category_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
