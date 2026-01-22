from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import sqlite3
import bcrypt
import jwt
import secrets
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

# Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ForgotPassword(BaseModel):
    email: str

class ResetPassword(BaseModel):
    token: str
    new_password: str

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

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

@app.post("/api/auth/register")
def register(user: UserCreate):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (user.email, user.username))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash password
    password_hash = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    # Create user
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (user.username, user.email, password_hash)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Create token
    token = create_access_token({"user_id": user_id, "username": user.username})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "username": user.username, "email": user.email}
    }

@app.post("/api/auth/login")
def login(user: UserLogin):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email, password_hash FROM users WHERE email = ?", (user.email,))
    db_user = cursor.fetchone()
    conn.close()
    
    if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user[3]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
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
def forgot_password(request: ForgotPassword):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id, username FROM users WHERE email = ?", (request.email,))
    user = cursor.fetchone()
    
    if not user:
        # Don't reveal if email exists or not for security
        conn.close()
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    
    # Store reset token
    cursor.execute(
        "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
        (user[0], reset_token, expires_at)
    )
    
    conn.commit()
    conn.close()
    
    # In a real application, you would send an email here
    # For demo purposes, we'll return the token (don't do this in production!)
    return {
        "message": "Password reset link sent to your email",
        "reset_token": reset_token  # Remove this in production
    }

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
    
    # Hash new password
    password_hash = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt())
    
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

@app.get("/api/tools")
def get_tools():
    return [
        {
            "id": 1,
            "name": "Docker",
            "slug": "docker",
            "description": "Container platform for building, shipping, and running applications",
            "homepage_url": "https://www.docker.com",
            "github_url": "https://github.com/moby/moby",
            "category": "Container",
            "license": "Apache-2.0",
            "pricing_model": "freemium",
            "logo_url": None,
            "github_stars": 68000,
            "github_forks": 18500,
            "last_commit_date": "2024-01-01T00:00:00",
            "ai_summary": "Docker revolutionized software deployment through containerization",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        },
        {
            "id": 2,
            "name": "Kubernetes",
            "slug": "kubernetes",
            "description": "Container orchestration platform for automating deployment and scaling",
            "homepage_url": "https://kubernetes.io",
            "github_url": "https://github.com/kubernetes/kubernetes",
            "category": "Container",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "logo_url": None,
            "github_stars": 105000,
            "github_forks": 38000,
            "last_commit_date": "2024-01-01T00:00:00",
            "ai_summary": "Kubernetes is the de facto standard for container orchestration",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
    ]

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
def enhanced_compare():
    return {"comparison": "AI comparison feature"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
