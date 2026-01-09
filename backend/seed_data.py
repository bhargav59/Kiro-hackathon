import requests
import json
from datetime import datetime
from sqlalchemy.orm import Session
from main import SessionLocal, Tool, User, create_slug
import bcrypt

def seed_sample_tools():
    """Seed the database with sample DevOps tools and demo user"""
    
    sample_tools = [
        {
            "name": "Docker",
            "description": "A comprehensive containerization platform that enables developers to package applications and their dependencies into lightweight, portable containers. Docker simplifies application deployment, scaling, and management across different environments while ensuring consistency from development to production.",
            "homepage_url": "https://www.docker.com",
            "github_url": "https://github.com/moby/moby",
            "category": "Container",
            "license": "Apache-2.0",
            "pricing_model": "freemium",
            "github_stars": 68000,
            "github_forks": 18500,
            "ai_summary": "Docker revolutionized software deployment through containerization, enabling consistent environments across development, testing, and production. It provides container orchestration, image management, and seamless integration with CI/CD pipelines. Docker's ecosystem includes Docker Hub for image sharing, Docker Compose for multi-container applications, and Docker Swarm for orchestration."
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
        },
        {
            "name": "Ansible",
            "description": "Simple, agentless automation platform for configuration management, application deployment, and task automation.",
            "homepage_url": "https://www.ansible.com",
            "github_url": "https://github.com/ansible/ansible",
            "category": "Infrastructure",
            "license": "GPL-3.0",
            "pricing_model": "freemium",
            "github_stars": 61000,
            "github_forks": 23800,
            "ai_summary": "Ansible simplifies IT automation with human-readable YAML playbooks. Its agentless architecture and extensive module library make it ideal for configuration management."
        },
        {
            "name": "GitHub Actions",
            "description": "CI/CD platform integrated with GitHub for automating software workflows directly from repositories.",
            "homepage_url": "https://github.com/features/actions",
            "github_url": "https://github.com/actions",
            "category": "CI/CD",
            "license": "MIT",
            "pricing_model": "freemium",
            "github_stars": 8500,
            "github_forks": 2100,
            "ai_summary": "GitHub Actions provides seamless CI/CD integration within GitHub repositories. It offers marketplace actions and matrix builds for comprehensive automation workflows."
        }
    ]
    
    db = SessionLocal()
    try:
        # Create demo user
        try:
            demo_user = db.query(User).filter(User.email == "demo@cloudengineered.com").first()
            if not demo_user:
                hashed_password = bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt())
                demo_user = User(
                    email="demo@cloudengineered.com",
                    name="Demo User",
                    hashed_password=hashed_password.decode('utf-8'),
                    is_active=True
                )
                db.add(demo_user)
                print("Added demo user: demo@cloudengineered.com / demo123")
        except Exception as e:
            print(f"Demo user creation error (may already exist): {e}")
        
        for tool_data in sample_tools:
            # Check if tool already exists
            existing_tool = db.query(Tool).filter(Tool.name == tool_data["name"]).first()
            if existing_tool:
                continue
            
            # Create slug
            slug = create_slug(tool_data["name"])
            
            # Create tool
            tool = Tool(
                name=tool_data["name"],
                slug=slug,
                description=tool_data["description"],
                homepage_url=tool_data["homepage_url"],
                github_url=tool_data["github_url"],
                category=tool_data["category"],
                license=tool_data["license"],
                pricing_model=tool_data["pricing_model"],
                github_stars=tool_data["github_stars"],
                github_forks=tool_data["github_forks"],
                ai_summary=tool_data["ai_summary"],
                last_commit_date=datetime.utcnow()
            )
            
            db.add(tool)
            print(f"Added tool: {tool_data['name']}")
        
        db.commit()
        print("Sample tools and demo user seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_tools()
