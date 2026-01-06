#!/usr/bin/env python3
"""
Script to enhance Docker tool details with comprehensive information
"""

import requests
import json
from datetime import datetime
from sqlalchemy.orm import Session
from main import SessionLocal, Tool

def enhance_docker_details():
    """Enhance Docker tool with comprehensive details"""
    
    db = SessionLocal()
    try:
        # Find Docker tool
        docker_tool = db.query(Tool).filter(Tool.name == "Docker").first()
        if not docker_tool:
            print("Docker tool not found in database")
            return
        
        # Enhanced Docker details
        enhanced_description = """A comprehensive containerization platform that enables developers to package applications and their dependencies into lightweight, portable containers. Docker simplifies application deployment, scaling, and management across different environments while ensuring consistency from development to production.

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
• Cloud Migration: Simplify cloud adoption with portable containers"""

        enhanced_ai_summary = """Docker revolutionized software deployment through containerization, enabling consistent environments across development, testing, and production. It provides container orchestration, image management, and seamless integration with CI/CD pipelines. 

Docker's ecosystem includes:
- Docker Hub: World's largest container registry with millions of images
- Docker Compose: Define and run multi-container applications with YAML
- Docker Desktop: Easy-to-use development environment for Mac and Windows
- Docker Swarm: Built-in orchestration for production deployments

Key benefits include resource efficiency (containers share OS kernel), rapid deployment (seconds vs minutes), microservices architecture support, and cross-platform compatibility. Docker has become essential for DevOps workflows, enabling practices like Infrastructure as Code, immutable deployments, and horizontal scaling.

Popular alternatives include Podman, containerd, and CRI-O, but Docker remains the most widely adopted containerization platform with extensive community support and enterprise features."""

        # Update Docker tool
        docker_tool.description = enhanced_description
        docker_tool.ai_summary = enhanced_ai_summary
        docker_tool.updated_at = datetime.utcnow()
        
        # Fetch real GitHub stats
        try:
            github_url = "https://api.github.com/repos/moby/moby"
            response = requests.get(github_url, timeout=10)
            if response.status_code == 200:
                github_data = response.json()
                docker_tool.github_stars = github_data.get("stargazers_count", docker_tool.github_stars)
                docker_tool.github_forks = github_data.get("forks_count", docker_tool.github_forks)
                if github_data.get("updated_at"):
                    docker_tool.last_commit_date = datetime.fromisoformat(
                        github_data["updated_at"].replace("Z", "+00:00")
                    )
                print(f"Updated GitHub stats: {docker_tool.github_stars} stars, {docker_tool.github_forks} forks")
        except Exception as e:
            print(f"Could not fetch GitHub stats: {e}")
        
        db.commit()
        print("Docker tool enhanced successfully!")
        
        # Display updated information
        print(f"\nEnhanced Docker Details:")
        print(f"Name: {docker_tool.name}")
        print(f"Category: {docker_tool.category}")
        print(f"License: {docker_tool.license}")
        print(f"Pricing: {docker_tool.pricing_model}")
        print(f"GitHub Stars: {docker_tool.github_stars:,}")
        print(f"GitHub Forks: {docker_tool.github_forks:,}")
        print(f"Description length: {len(docker_tool.description)} characters")
        print(f"AI Summary length: {len(docker_tool.ai_summary)} characters")
        
    except Exception as e:
        print(f"Error enhancing Docker details: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    enhance_docker_details()
