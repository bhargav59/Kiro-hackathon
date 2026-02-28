#!/usr/bin/env python3
"""
Initialize database without dependencies
"""
import sqlite3
import os

def init_database():
    """Initialize SQLite database with required tables"""
    db_path = "cloudengineered.db"

    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tools table
    cursor.execute("""
        CREATE TABLE tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR UNIQUE NOT NULL,
            slug VARCHAR UNIQUE NOT NULL,
            description TEXT,
            homepage_url VARCHAR,
            github_url VARCHAR,
            category VARCHAR,
            license VARCHAR,
            pricing_model VARCHAR,
            logo_url VARCHAR,
            github_stars INTEGER DEFAULT 0,
            github_forks INTEGER DEFAULT 0,
            last_commit_date DATETIME,
            ai_summary TEXT,
            health_score INTEGER DEFAULT 0,
            health_data TEXT,
            last_health_check DATETIME,
            created_at DATETIME,
            updated_at DATETIME
        )
    """)
    print("Created tools table")

    # Create users table
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR UNIQUE NOT NULL,
            username VARCHAR UNIQUE NOT NULL,
            password_hash VARCHAR,
            github_id VARCHAR,
            avatar_url VARCHAR,
            bio TEXT,
            is_admin BOOLEAN DEFAULT 0,
            subscription_plan VARCHAR DEFAULT 'free',
            created_at DATETIME
        )
    """)
    print("Created users table")

    # Create reviews table
    cursor.execute("""
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_id INTEGER,
            user_id INTEGER,
            rating INTEGER,
            content TEXT,
            helpful_count INTEGER DEFAULT 0,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY (tool_id) REFERENCES tools (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    print("Created reviews table")

    # Create user_stacks table
    cursor.execute("""
        CREATE TABLE user_stacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tool_id INTEGER,
            added_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (tool_id) REFERENCES tools (id)
        )
    """)
    print("Created user_stacks table")

    # Create review_votes table
    cursor.execute("""
        CREATE TABLE review_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER,
            user_id INTEGER,
            is_helpful BOOLEAN,
            created_at DATETIME,
            FOREIGN KEY (review_id) REFERENCES reviews (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    print("Created review_votes table")

    # Create blogs table
    cursor.execute("""
        CREATE TABLE blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR NOT NULL,
            slug VARCHAR UNIQUE NOT NULL,
            content TEXT,
            author_id INTEGER,
            cover_image_url VARCHAR,
            tags TEXT,
            published BOOLEAN DEFAULT 0,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY (author_id) REFERENCES users (id)
        )
    """)
    print("Created blogs table")

    # Create usage_logs table
    cursor.execute("""
        CREATE TABLE usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action VARCHAR NOT NULL,
            created_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    print("Created usage_logs table")

    # Create email_subscribers table
    cursor.execute("""
        CREATE TABLE email_subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR UNIQUE NOT NULL,
            name VARCHAR,
            source VARCHAR,
            subscribed_at DATETIME,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    print("Created email_subscribers table")

    # Create comparison_pages table
    cursor.execute("""
        CREATE TABLE comparison_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_a_id INTEGER,
            tool_b_id INTEGER,
            slug VARCHAR UNIQUE NOT NULL,
            title VARCHAR NOT NULL,
            content TEXT,
            meta_description VARCHAR,
            views INTEGER DEFAULT 0,
            generated_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY (tool_a_id) REFERENCES tools (id),
            FOREIGN KEY (tool_b_id) REFERENCES tools (id)
        )
    """)
    print("Created comparison_pages table")

    conn.commit()
    conn.close()
    print(f"Database initialized: {db_path}")

if __name__ == "__main__":
    init_database()
