#!/usr/bin/env python3
"""
Simple seed script without external dependencies
"""
import sqlite3
import os
from datetime import datetime

def create_slug(name):
    return name.lower().replace(" ", "-").replace(".", "").replace("/", "-")

def seed_database():
    # Database path
    db_path = "cloudengineered.db"
    
    # Enhanced Docker data
    docker_data = {
        "name": "Docker",
        "slug": create_slug("Docker"),
        "description": """A comprehensive containerization platform that enables developers to package applications and their dependencies into lightweight, portable containers. Docker simplifies application deployment, scaling, and management across different environments while ensuring consistency from development to production.

Key Features:
• Container Runtime: Efficient container execution with resource isolation
• Image Management: Build, store, and distribute container images via Docker Hub
• Docker Compose: Multi-container application orchestration
• Docker Swarm: Native clustering and orchestration capabilities
• Cross-platform Support: Works on Linux, Windows, and macOS
• CI/CD Integration: Seamless integration with popular CI/CD pipelines

Use Cases:
• Microservices Architecture: Containerize individual services for better scalability
• Development Environment Standardization: Ensure consistent dev/test/prod environments
• Application Modernization: Migrate legacy applications to containerized deployments
• Cloud Migration: Simplify cloud adoption with portable containers

Pricing Tiers:
• Docker Personal: Free for personal use, small businesses, education
• Docker Pro: $5/month per user - includes unlimited private repositories
• Docker Team: $7/month per user - adds team management and audit logs
• Docker Business: $21/month per user - enterprise features and support""",
        "homepage_url": "https://www.docker.com",
        "github_url": "https://github.com/moby/moby",
        "category": "Container",
        "license": "Apache-2.0",
        "pricing_model": "freemium",
        "github_stars": 68000,
        "github_forks": 18500,
        "ai_summary": """Docker revolutionized software deployment through containerization, enabling consistent environments across development, testing, and production. It provides container orchestration, image management, and seamless integration with CI/CD pipelines.

Docker's ecosystem includes:
- Docker Hub: World's largest container registry with millions of images
- Docker Compose: Define and run multi-container applications with YAML
- Docker Desktop: Easy-to-use development environment for Mac and Windows
- Docker Swarm: Built-in orchestration for production deployments

Key benefits include resource efficiency (containers share OS kernel), rapid deployment (seconds vs minutes), microservices architecture support, and cross-platform compatibility. Docker has become essential for DevOps workflows, enabling practices like Infrastructure as Code, immutable deployments, and horizontal scaling.

Popular alternatives include Podman, containerd, and CRI-O, but Docker remains the most widely adopted containerization platform with extensive community support and enterprise features.""",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if Docker already exists
        cursor.execute("SELECT id FROM tools WHERE name = ?", (docker_data["name"],))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing Docker entry
            cursor.execute("""
                UPDATE tools SET 
                    description = ?, 
                    ai_summary = ?, 
                    github_stars = ?, 
                    github_forks = ?,
                    updated_at = ?
                WHERE name = ?
            """, (
                docker_data["description"],
                docker_data["ai_summary"],
                docker_data["github_stars"],
                docker_data["github_forks"],
                docker_data["updated_at"],
                docker_data["name"]
            ))
            print(f"✅ Updated Docker tool with enhanced details")
        else:
            # Insert new Docker entry
            cursor.execute("""
                INSERT INTO tools (
                    name, slug, description, homepage_url, github_url, 
                    category, license, pricing_model, github_stars, 
                    github_forks, ai_summary, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                docker_data["name"], docker_data["slug"], docker_data["description"],
                docker_data["homepage_url"], docker_data["github_url"], docker_data["category"],
                docker_data["license"], docker_data["pricing_model"], docker_data["github_stars"],
                docker_data["github_forks"], docker_data["ai_summary"], 
                docker_data["created_at"], docker_data["updated_at"]
            ))
            print(f"✅ Added Docker tool with enhanced details")
        
        conn.commit()
        
        # Verify the data
        cursor.execute("SELECT name, github_stars, LENGTH(description), LENGTH(ai_summary) FROM tools WHERE name = ?", (docker_data["name"],))
        result = cursor.fetchone()
        if result:
            name, stars, desc_len, summary_len = result
            print(f"📊 Verification: {name} - {stars:,} stars, {desc_len} char description, {summary_len} char summary")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🌱 Seeding database with enhanced Docker details...")
    success = seed_database()
    if success:
        print("🎉 Database seeding completed successfully!")
    else:
        print("💥 Database seeding failed!")
