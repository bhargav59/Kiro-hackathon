#!/usr/bin/env python3
"""
Complete seed script without external dependencies
"""
import sqlite3
import os
from datetime import datetime

def create_slug(name):
    return name.lower().replace(" ", "-").replace(".", "").replace("/", "-")

def seed_all_tools():
    """Seed database with all sample tools"""
    
    sample_tools = [
        {
            "name": "Docker",
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
• Cloud Migration: Simplify cloud adoption with portable containers""",
            "homepage_url": "https://www.docker.com",
            "github_url": "https://github.com/moby/moby",
            "category": "Container",
            "license": "Apache-2.0",
            "pricing_model": "freemium",
            "github_stars": 68000,
            "github_forks": 18500,
            "ai_summary": "Docker revolutionized software deployment through containerization, enabling consistent environments across development, testing, and production. It provides container orchestration, image management, and seamless integration with CI/CD pipelines."
        },
        {
            "name": "Kubernetes",
            "description": "An open-source container orchestration platform for automating deployment, scaling, and management of containerized applications.",
            "homepage_url": "https://kubernetes.io",
            "github_url": "https://github.com/kubernetes/kubernetes",
            "category": "Container",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 105000,
            "github_forks": 38000,
            "ai_summary": "Kubernetes is the de facto standard for container orchestration, providing powerful features for scaling, service discovery, and managing complex distributed applications."
        },
        {
            "name": "Terraform",
            "description": "Infrastructure as Code tool for building, changing, and versioning infrastructure safely and efficiently.",
            "homepage_url": "https://www.terraform.io",
            "github_url": "https://github.com/hashicorp/terraform",
            "category": "Infrastructure",
            "license": "MPL-2.0",
            "pricing_model": "freemium",
            "github_stars": 41000,
            "github_forks": 9400,
            "ai_summary": "Terraform enables infrastructure as code with a declarative configuration language. It supports multiple cloud providers and maintains state for reliable infrastructure management."
        },
        {
            "name": "Jenkins",
            "description": "An open-source automation server for building, testing, and deploying software projects.",
            "homepage_url": "https://www.jenkins.io",
            "github_url": "https://github.com/jenkinsci/jenkins",
            "category": "CI/CD",
            "license": "MIT",
            "pricing_model": "free",
            "github_stars": 22000,
            "github_forks": 8600,
            "ai_summary": "Jenkins is a widely-adopted CI/CD platform with extensive plugin ecosystem. It provides flexible pipeline configuration and integrates with virtually any tool in the DevOps toolchain."
        },
        {
            "name": "Prometheus",
            "description": "A monitoring and alerting toolkit designed for reliability and scalability of cloud-native applications.",
            "homepage_url": "https://prometheus.io",
            "github_url": "https://github.com/prometheus/prometheus",
            "category": "Monitoring",
            "license": "Apache-2.0",
            "pricing_model": "free",
            "github_stars": 52000,
            "github_forks": 8900,
            "ai_summary": "Prometheus provides powerful metrics collection and querying capabilities with a time-series database. It's designed for dynamic cloud environments with service discovery."
        },
        {
            "name": "Grafana",
            "description": "Open-source analytics and interactive visualization web application for monitoring and observability.",
            "homepage_url": "https://grafana.com",
            "github_url": "https://github.com/grafana/grafana",
            "category": "Monitoring",
            "license": "AGPL-3.0",
            "pricing_model": "freemium",
            "github_stars": 60000,
            "github_forks": 11800,
            "ai_summary": "Grafana excels at creating beautiful, interactive dashboards for monitoring data. It supports numerous data sources and provides advanced visualization capabilities."
        }
    ]
    
    db_path = "cloudengineered.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for tool_data in sample_tools:
            # Check if tool already exists
            cursor.execute("SELECT id FROM tools WHERE name = ?", (tool_data["name"],))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing tool
                cursor.execute("""
                    UPDATE tools SET 
                        description = ?, 
                        ai_summary = ?, 
                        github_stars = ?, 
                        github_forks = ?,
                        updated_at = ?
                    WHERE name = ?
                """, (
                    tool_data["description"],
                    tool_data["ai_summary"],
                    tool_data["github_stars"],
                    tool_data["github_forks"],
                    datetime.utcnow().isoformat(),
                    tool_data["name"]
                ))
                print(f"✅ Updated {tool_data['name']}")
            else:
                # Insert new tool
                cursor.execute("""
                    INSERT INTO tools (
                        name, slug, description, homepage_url, github_url, 
                        category, license, pricing_model, github_stars, 
                        github_forks, ai_summary, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tool_data["name"], create_slug(tool_data["name"]), tool_data["description"],
                    tool_data["homepage_url"], tool_data["github_url"], tool_data["category"],
                    tool_data["license"], tool_data["pricing_model"], tool_data["github_stars"],
                    tool_data["github_forks"], tool_data["ai_summary"], 
                    datetime.utcnow().isoformat(), datetime.utcnow().isoformat()
                ))
                print(f"✅ Added {tool_data['name']}")
        
        conn.commit()
        
        # Verify the data
        cursor.execute("SELECT COUNT(*) FROM tools")
        count = cursor.fetchone()[0]
        print(f"📊 Database now has {count} tools")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🌱 Seeding database with all sample tools...")
    success = seed_all_tools()
    if success:
        print("🎉 Database seeding completed successfully!")
    else:
        print("💥 Database seeding failed!")
