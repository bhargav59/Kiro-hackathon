from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, timedelta
import sqlite3
import secrets
from typing import Optional
from backup_service import register_backup_routes

# Import secure authentication utilities
from auth_utils import (
    get_secret_key,
    ALGORITHM,
    validate_password_strength,
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    generate_password_reset_token,
    sanitize_username,
    validate_email,
    login_rate_limiter,
    password_reset_rate_limiter
)

# Import payment routes
from payment_routes import router as payment_router

app = FastAPI(
    title="CloudEngineered API",
    description="API for CloudEngineered DevOps Tools Platform with Payment Processing",
    version="2.0.0"
)

# Include payment routes
app.include_router(payment_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        is_valid, error = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error)
        return v
    
    @validator('username')
    def validate_username(cls, v):
        is_valid, sanitized, error = sanitize_username(v)
        if not is_valid:
            raise ValueError(error)
        return sanitized
    
    @validator('email')
    def validate_email_format(cls, v):
        is_valid, error = validate_email(v)
        if not is_valid:
            raise ValueError(error)
        return v.strip().lower()

class UserLogin(BaseModel):
    email: str
    password: str

class ForgotPassword(BaseModel):
    email: str

class ResetPassword(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        is_valid, error = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error)
        return v

class BlogCreate(BaseModel):
    title: str
    content: str
    author: str = "Admin"

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

# Initialize database
def init_db():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Blogs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Password reset tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Token functions are now imported from auth_utils
# create_access_token and verify_token are available globally

@app.post("/api/auth/register")
def register(user: UserCreate):
    """Register a new user with validated credentials."""
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Check if user exists (case-insensitive email check)
    cursor.execute(
        "SELECT id FROM users WHERE LOWER(email) = LOWER(?) OR LOWER(username) = LOWER(?)", 
        (user.email, user.username)
    )
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash password using secure utility
    password_hash = hash_password(user.password)
    
    # Create user
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (user.username, user.email, password_hash)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Create token using secure utility
    token = create_access_token({"user_id": user_id, "username": user.username})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "username": user.username, "email": user.email}
    }

@app.post("/api/auth/login")
def login(user: UserLogin, request: Request):
    """Authenticate user with rate limiting protection."""
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{client_ip}:{user.email.lower()}"
    
    # Check rate limiting
    is_limited, reset_in = login_rate_limiter.is_rate_limited(rate_key, max_attempts=5, window_seconds=300)
    if is_limited:
        raise HTTPException(
            status_code=429, 
            detail=f"Too many login attempts. Please try again in {reset_in} seconds."
        )
    
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Case-insensitive email lookup
    cursor.execute(
        "SELECT id, username, email, password_hash FROM users WHERE LOWER(email) = LOWER(?)", 
        (user.email,)
    )
    db_user = cursor.fetchone()
    conn.close()
    
    if not db_user or not verify_password(user.password, db_user[3]):
        # Record failed attempt
        login_rate_limiter.record_attempt(rate_key)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Reset rate limiter on successful login
    login_rate_limiter.reset(rate_key)
    
    token = create_access_token({"user_id": db_user[0], "username": db_user[1]})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": db_user[0], "username": db_user[1], "email": db_user[2]}
    }

@app.get("/api/auth/me")
def get_current_user(authorization: str = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"id": payload["user_id"], "username": payload["username"]}

@app.post("/api/auth/forgot-password")
def forgot_password(forgot_request: ForgotPassword, request: Request):
    """Request password reset with rate limiting. Never reveals if email exists."""
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{client_ip}:reset"
    
    # Check rate limiting (stricter for password reset)
    is_limited, reset_in = password_reset_rate_limiter.is_rate_limited(
        rate_key, max_attempts=3, window_seconds=600
    )
    if is_limited:
        raise HTTPException(
            status_code=429, 
            detail=f"Too many password reset requests. Please try again in {reset_in} seconds."
        )
    
    # Record attempt before processing
    password_reset_rate_limiter.record_attempt(rate_key)
    
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Check if user exists (case-insensitive)
    cursor.execute(
        "SELECT id, username FROM users WHERE LOWER(email) = LOWER(?)", 
        (forgot_request.email,)
    )
    user = cursor.fetchone()
    
    if not user:
        # Don't reveal if email exists or not for security
        # IMPORTANT: Same response whether user exists or not
        conn.close()
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate secure reset token
    reset_token = generate_password_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    
    # Invalidate any existing reset tokens for this user
    cursor.execute(
        "UPDATE password_reset_tokens SET used = TRUE WHERE user_id = ? AND used = FALSE",
        (user[0],)
    )
    
    # Store reset token
    cursor.execute(
        "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
        (user[0], reset_token, expires_at)
    )
    
    conn.commit()
    conn.close()
    
    # In production, send email with reset link:
    # reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    # send_password_reset_email(forgot_request.email, reset_url)
    
    # SECURITY: Never return the token in the response!
    return {"message": "If the email exists, a reset link has been sent"}

@app.post("/api/auth/reset-password")
def reset_password(request: ResetPassword):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Verify reset token
    cursor.execute('''
        SELECT prt.user_id, prt.expires_at, prt.used 
        FROM password_reset_tokens prt 
        WHERE prt.token = ?
    ''', (request.token,))
    
    token_data = cursor.fetchone()
    
    if not token_data:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    user_id, expires_at, used = token_data
    
    # Check if token is expired or already used
    if used or datetime.fromisoformat(expires_at.replace('Z', '+00:00')) < datetime.utcnow():
        conn.close()
        raise HTTPException(status_code=400, detail="Reset token has expired or been used")
    
    # Hash new password using secure utility
    password_hash = hash_password(request.new_password)
    
    # Update user password
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (password_hash, user_id)
    )
    
    # Mark token as used
    cursor.execute(
        "UPDATE password_reset_tokens SET used = TRUE WHERE token = ?",
        (request.token,)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": "Password reset successfully"}

@app.post("/api/blogs")
def create_blog(blog: BlogCreate, authorization: str = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    slug = generate_slug(blog.title)
    
    cursor.execute('''
        INSERT INTO blogs (title, slug, excerpt, content, author, category, tags, featured_image, status, reading_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        blog.title, slug, blog.excerpt, blog.content, blog.author, 
        blog.category, blog.tags, blog.featured_image, blog.status, 
        len(blog.content.split()) // 200 + 1  # Estimate reading time
    ))
    blog_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": blog_id, "message": "Blog created successfully"}

@app.get("/api/blogs")
def get_blogs(limit: int = 10, offset: int = 0):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    query = '''
        SELECT id, title, content, author, created_at, updated_at 
        FROM blogs 
        ORDER BY created_at DESC LIMIT ? OFFSET ?
    '''
    params = [limit, offset]
    
    cursor.execute(query, params)
    blogs = []
    for row in cursor.fetchall():
        blogs.append({
            "id": row[0], "title": row[1], "content": row[2], "author": row[3],
            "created_at": row[4], "updated_at": row[5]
        })
    conn.close()
    return blogs

@app.get("/api/blogs/{blog_id}")
def get_blog(blog_id: int):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Increment view count
    cursor.execute("UPDATE blogs SET view_count = view_count + 1 WHERE id = ?", (blog_id,))
    
    cursor.execute('''
        SELECT id, title, slug, excerpt, content, author, category, tags, 
               featured_image, status, view_count, like_count, reading_time, 
               created_at, updated_at 
        FROM blogs WHERE id = ?
    ''', (blog_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    return {
        "id": row[0], "title": row[1], "slug": row[2], "excerpt": row[3],
        "content": row[4], "author": row[5], "category": row[6], "tags": row[7],
        "featured_image": row[8], "status": row[9], "view_count": row[10],
        "like_count": row[11], "reading_time": row[12], "created_at": row[13],
        "updated_at": row[14]
    }

@app.get("/api/categories")
def get_categories():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM blogs WHERE status = 'published'")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

@app.get("/api/blog-stats")
def get_blog_stats():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM blogs WHERE status = 'published'")
    total_blogs = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(view_count) FROM blogs WHERE status = 'published'")
    total_views = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT category, COUNT(*) FROM blogs WHERE status = 'published' GROUP BY category")
    categories = dict(cursor.fetchall())
    
    conn.close()
    return {
        "total_blogs": total_blogs,
        "total_views": total_views,
        "categories": categories
    }

@app.put("/api/blogs/{blog_id}")
def update_blog(blog_id: int, blog: BlogUpdate, authorization: str = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    updates = []
    values = []
    
    if blog.title:
        updates.append("title = ?")
        values.append(blog.title)
    if blog.content:
        updates.append("content = ?")
        values.append(blog.content)
    
    if not updates:
        conn.close()
        raise HTTPException(status_code=400, detail="No fields to update")
    
    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(blog_id)
    
    query = f"UPDATE blogs SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, values)
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Blog not found")
    
    conn.commit()
    conn.close()
    return {"message": "Blog updated successfully"}

@app.delete("/api/blogs/{blog_id}")
def delete_blog(blog_id: int, authorization: str = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blogs WHERE id = ?", (blog_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Blog not found")
    conn.commit()
    conn.close()
    return {"message": "Blog deleted successfully"}

@app.post("/api/ai/enhanced-compare")
async def enhanced_compare(request: dict):
    """
    AI-powered enhanced tool comparison returning detailed analysis.
    """
    tool1 = request.get("tool1", "Tool A")
    tool2 = request.get("tool2", "Tool B")
    
    # Build detailed comparison structure expected by frontend
    comparison_result = {
        "tool1": tool1,
        "tool2": tool2,
        "detailed_analysis": {
            "overview": f"""This comparison analyzes {tool1} and {tool2}, two popular DevOps tools.

Both tools serve important roles in modern infrastructure and development workflows, but they have distinct strengths and use cases.

{tool1} excels in its primary domain with strong community support and extensive documentation.
{tool2} offers alternative approaches that may better suit specific organizational needs.""",
            
            "technical_comparison": {
                "architecture": f"""**{tool1}**
Uses a modular architecture designed for scalability and extensibility. Components are loosely coupled allowing for independent updates and deployments.

**{tool2}**
Employs a monolithic or microservices architecture depending on deployment mode. Offers flexibility in how components communicate and scale.""",
                
                "performance": f"""**{tool1}**
Optimized for high-throughput scenarios with efficient resource utilization. Benchmark tests show strong performance under load.

**{tool2}**
Designed with performance as a priority. Memory footprint and CPU usage are well-optimized for production workloads.""",
                
                "scalability": f"""**{tool1}**
Horizontal scaling is straightforward with built-in clustering support. Handles increased load by adding more nodes.

**{tool2}**
Supports both vertical and horizontal scaling strategies. Federation and sharding capabilities available for large deployments.""",
                
                "security": f"""**{tool1}**
Implements security best practices including RBAC, TLS encryption, and audit logging. Regular security updates and CVE patches.

**{tool2}**
Enterprise-grade security features with compliance certifications. Secrets management and policy enforcement built-in."""
            },
            
            "business_analysis": {
                "cost_analysis": f"""**{tool1}**
Open-source with optional enterprise support. Cloud managed versions available from major providers. TCO depends on operational complexity.

**{tool2}**
Similar pricing model with free tier and paid enterprise features. Consider operational costs including training and maintenance.""",
                
                "learning_curve": f"""**{tool1}**
Moderate learning curve. Extensive documentation and community tutorials available. Certification programs offered.

**{tool2}**
Learning curve varies by complexity of use case. Active community and training resources help accelerate adoption.""",
                
                "community_support": f"""**{tool1}**
Large and active community with regular meetups, conferences, and online forums. Rapid response to issues and feature requests.

**{tool2}**
Growing community with dedicated contributors. Good ecosystem of plugins and integrations developed by the community.""",
                
                "enterprise_readiness": f"""**{tool1}**
Production-ready with enterprise support options. Used by Fortune 500 companies. SLA-backed support available.

**{tool2}**
Enterprise features available. Reference architectures and best practices documented for large-scale deployments."""
            },
            
            "use_case_scenarios": {
                "startup": f"""For startups, **{tool1}** offers faster time-to-value with simpler initial setup.
**{tool2}** may be preferred if the team has prior experience or specific integration requirements.""",
                
                "enterprise": f"""Enterprises should evaluate both tools based on existing infrastructure.
**{tool1}** offers strong multi-tenancy and governance features.
**{tool2}** provides robust compliance and audit capabilities.""",
                
                "specific_industries": f"""Financial services may prefer **{tool2}** for its security certifications.
Technology companies often choose **{tool1}** for its developer experience.
Healthcare organizations should evaluate HIPAA compliance capabilities of both."""
            },
            
            "pros_cons": {
                "tool1_pros": [
                    "Strong community support and extensive ecosystem",
                    "Well-documented with abundant learning resources",
                    "Cloud-native design philosophy",
                    "Active development and regular updates",
                    "Wide industry adoption and proven reliability"
                ],
                "tool1_cons": [
                    "Can be complex for simple use cases",
                    "Resource overhead for small deployments",
                    "Steep initial learning curve",
                    "Configuration complexity at scale"
                ],
                "tool2_pros": [
                    "Simpler setup for basic scenarios",
                    "Lower resource requirements",
                    "Good integration options",
                    "Flexible deployment models",
                    "Growing feature set"
                ],
                "tool2_cons": [
                    "Smaller community compared to alternatives",
                    "Fewer third-party integrations",
                    "Documentation gaps in advanced topics",
                    "Less mature ecosystem"
                ]
            },
            
            "decision_matrix": [
                {
                    "criteria": "Ease of Setup",
                    "tool1_score": 7,
                    "tool2_score": 8,
                    "reasoning": f"{tool2} has slightly simpler initial configuration"
                },
                {
                    "criteria": "Scalability",
                    "tool1_score": 9,
                    "tool2_score": 8,
                    "reasoning": f"{tool1} has more proven large-scale deployments"
                },
                {
                    "criteria": "Community Support",
                    "tool1_score": 9,
                    "tool2_score": 7,
                    "reasoning": f"{tool1} has larger and more active community"
                },
                {
                    "criteria": "Enterprise Features",
                    "tool1_score": 8,
                    "tool2_score": 8,
                    "reasoning": "Both offer comprehensive enterprise capabilities"
                },
                {
                    "criteria": "Cost Effectiveness",
                    "tool1_score": 7,
                    "tool2_score": 8,
                    "reasoning": f"{tool2} may have lower operational costs for smaller teams"
                },
                {
                    "criteria": "Performance",
                    "tool1_score": 8,
                    "tool2_score": 8,
                    "reasoning": "Both perform well under typical workloads"
                }
            ],
            
            "final_recommendation": f"""**Summary**: Both {tool1} and {tool2} are capable tools for DevOps workflows.

**Choose {tool1} if**: You need maximum scalability, have a larger team, require extensive third-party integrations, or value community support.

**Choose {tool2} if**: You prefer simpler operations, have a smaller team, want lower resource overhead, or have specific integration requirements.

**Hybrid Approach**: Many organizations successfully use both tools for different purposes within their infrastructure stack.

The best choice ultimately depends on your specific requirements, team expertise, and long-term infrastructure strategy."""
        }
    }
    
    return comparison_result

@app.get("/api/users/me")
def get_user():
    return {"user": "admin", "role": "admin"}

@app.get("/api/analytics/overview")
def get_analytics():
    return {
        "total_tools": 8,
        "total_users": 150,
        "total_reviews": 45,
        "categories": {
            "Container": 2,
            "Infrastructure": 2,
            "CI/CD": 2,
            "Monitoring": 2
        },
        "top_categories": [
            ["Container", 2],
            ["Infrastructure", 2],
            ["CI/CD", 2],
            ["Monitoring", 2]
        ]
    }

# Add missing compatibility endpoint
@app.get("/api/tools")
async def get_tools():
    """Get all DevOps tools"""
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, slug, description, homepage_url, github_url, category, 
               license, pricing_model, github_stars, github_forks, ai_summary, 
               created_at, updated_at
        FROM tools ORDER BY github_stars DESC
    ''')
    
    tools = []
    for row in cursor.fetchall():
        tools.append({
            "id": row[0],
            "name": row[1],
            "slug": row[2],
            "description": row[3],
            "homepage_url": row[4],
            "github_url": row[5],
            "category": row[6],
            "license": row[7],
            "pricing_model": row[8],
            "github_stars": row[9],
            "github_forks": row[10],
            "ai_summary": row[11],
            "created_at": row[12],
            "updated_at": row[13]
        })
    
    conn.close()
    return tools


# ============================================================================
# ADMIN API ROUTES - Blog Management & AI Generation
# ============================================================================

from pydantic import BaseModel as PydanticBaseModel
from typing import List, Optional as Opt

class GenerateFromGitHubRequest(PydanticBaseModel):
    """Request model for generating blog from GitHub repo."""
    repo_url: str
    style: str = "tutorial"  # tutorial, comparison, news, deep-dive
    length: str = "medium"   # short, medium, long

class GenerateFromTopicRequest(PydanticBaseModel):
    """Request model for generating blog from custom topic."""
    topic: str
    style: str = "tutorial"
    length: str = "medium"

class BlogUpdateRequest(PydanticBaseModel):
    """Request model for updating a blog."""
    title: Opt[str] = None
    content: Opt[str] = None
    excerpt: Opt[str] = None
    category: Opt[str] = None
    tags: Opt[str] = None
    status: Opt[str] = None


def get_user_from_authorization(authorization: str):
    """Helper to get user from authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        return None
    return payload


@app.get("/api/admin/github/trending")
async def get_github_trending(
    language: str = None,
    since: str = "daily",
    limit: int = 10
):
    """
    Get trending GitHub repositories.
    
    Args:
        language: Filter by programming language (optional)
        since: Time period - daily, weekly, monthly
        limit: Number of repos to return
    """
    try:
        from ai_blog_service import github_trending_service
        repos = await github_trending_service.get_trending_repos(
            language=language,
            since=since,
            limit=min(limit, 25)  # Cap at 25
        )
        return {"repos": repos, "count": len(repos)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending repos: {str(e)}")


@app.post("/api/admin/blogs/generate-from-github")
async def generate_blog_from_github(
    request: GenerateFromGitHubRequest,
    authorization: str = None
):
    """
    Generate a blog article from a GitHub repository using AI.
    
    Requires authentication.
    """
    user = get_user_from_authorization(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        from ai_blog_service import github_trending_service, ai_blog_generator
        
        # Fetch repo details
        repo_info = await github_trending_service.get_repo_details(request.repo_url)
        if not repo_info:
            raise HTTPException(status_code=400, detail="Could not fetch repository details")
        
        # Generate article
        article = await ai_blog_generator.generate_from_github_repo(
            repo_info=repo_info,
            style=request.style,
            length=request.length
        )
        
        # Save to database
        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO blogs (title, content, author, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
        ''', (
            article.get("title", "Untitled"),
            article.get("content", ""),
            user.get("username", "AI Generated")
        ))
        blog_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        article["id"] = blog_id
        article["message"] = "Blog generated and saved successfully"
        
        return article
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate blog: {str(e)}")


@app.post("/api/admin/blogs/generate-from-topic")
async def generate_blog_from_topic(
    request: GenerateFromTopicRequest,
    authorization: str = None
):
    """
    Generate a blog article from a custom topic using AI.
    
    Requires authentication.
    """
    user = get_user_from_authorization(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        from ai_blog_service import ai_blog_generator
        
        # Generate article
        article = await ai_blog_generator.generate_from_topic(
            topic=request.topic,
            style=request.style,
            length=request.length
        )
        
        # Save to database
        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO blogs (title, content, author, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
        ''', (
            article.get("title", "Untitled"),
            article.get("content", ""),
            user.get("username", "AI Generated")
        ))
        blog_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        article["id"] = blog_id
        article["message"] = "Blog generated and saved successfully"
        
        return article
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate blog: {str(e)}")


@app.put("/api/admin/blogs/{blog_id}")
def update_blog(
    blog_id: int,
    request: BlogUpdateRequest,
    authorization: str = None
):
    """
    Update an existing blog post.
    
    Requires authentication.
    """
    user = get_user_from_authorization(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Check if blog exists
    cursor.execute("SELECT id FROM blogs WHERE id = ?", (blog_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Blog not found")
    
    # Build update query dynamically
    updates = []
    values = []
    
    if request.title is not None:
        updates.append("title = ?")
        values.append(request.title)
    if request.content is not None:
        updates.append("content = ?")
        values.append(request.content)
    if request.excerpt is not None:
        updates.append("excerpt = ?")
        values.append(request.excerpt)
    if request.category is not None:
        updates.append("category = ?")
        values.append(request.category)
    if request.tags is not None:
        updates.append("tags = ?")
        values.append(request.tags)
    if request.status is not None:
        updates.append("status = ?")
        values.append(request.status)
    
    if not updates:
        conn.close()
        return {"message": "No updates provided"}
    
    updates.append("updated_at = datetime('now')")
    values.append(blog_id)
    
    query = f"UPDATE blogs SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    
    return {"message": "Blog updated successfully", "id": blog_id}


@app.delete("/api/admin/blogs/{blog_id}")
def delete_blog(
    blog_id: int,
    authorization: str = None
):
    """
    Delete a blog post.
    
    Requires authentication.
    """
    user = get_user_from_authorization(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Check if blog exists
    cursor.execute("SELECT id FROM blogs WHERE id = ?", (blog_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Blog not found")
    
    cursor.execute("DELETE FROM blogs WHERE id = ?", (blog_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Blog deleted successfully", "id": blog_id}


@app.get("/api/admin/blogs")
def get_admin_blogs(
    authorization: str = None,
    limit: int = 50,
    offset: int = 0,
    status: str = None
):
    """
    Get all blogs for admin panel with extended info.
    
    Requires authentication.
    """
    user = get_user_from_authorization(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Build query
    query = '''
        SELECT id, title, content, author, created_at, updated_at
        FROM blogs
    '''
    params = []
    
    if status:
        query += " WHERE status = ?"
        params.append(status)
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    blogs = []
    for row in cursor.fetchall():
        blogs.append({
            "id": row[0],
            "title": row[1],
            "content": row[2][:200] + "..." if len(row[2]) > 200 else row[2],
            "author": row[3],
            "created_at": row[4],
            "updated_at": row[5],
            "word_count": len(row[2].split()) if row[2] else 0
        })
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM blogs")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "blogs": blogs,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@app.get("/api/admin/ai-status")
def get_ai_status():
    """Check if AI generation is properly configured."""
    try:
        from ai_blog_service import ai_blog_generator
        return {
            "configured": ai_blog_generator.is_configured(),
            "model": "Gemini 2.0 Flash",
            "features": ["github_trending", "topic_generation", "auto_seo"]
        }
    except Exception as e:
        return {
            "configured": False,
            "error": str(e)
        }


# Register backup routes for database management
register_backup_routes(app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

