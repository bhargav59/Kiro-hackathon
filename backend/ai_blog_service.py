"""
AI Blog Generation Service for CloudEngineered Platform

This module provides:
- GitHub Trending repository fetching
- AI-powered blog article generation using Gemini
- Automated SEO-optimized content creation
"""

import os
import re
import json
import aiohttp
from datetime import datetime
from typing import Optional, List, Dict, Any

# Try to import Gemini AI (may fail on Python 3.14)
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except (ImportError, TypeError) as e:
    print(f"Warning: google-generativeai not available: {e}")
    genai = None
    GENAI_AVAILABLE = False

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GENAI_AVAILABLE and GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-api-key":
    genai.configure(api_key=GEMINI_API_KEY)


class GitHubTrendingService:
    """
    Service for fetching trending repositories from GitHub.
    """
    
    GITHUB_API_BASE = "https://api.github.com"
    
    async def get_trending_repos(
        self, 
        language: Optional[str] = None,
        since: str = "daily",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch trending repositories from GitHub.
        
        Args:
            language: Filter by programming language
            since: Time range - "daily", "weekly", "monthly"
            limit: Maximum number of repos to return
            
        Returns:
            List of trending repository data
        """
        # Build search query for popular repos
        query_parts = ["stars:>1000"]
        
        if language:
            query_parts.append(f"language:{language}")
        
        # Time-based filter
        time_filters = {
            "daily": "pushed:>2024-01-01",  # Actively maintained
            "weekly": "pushed:>2024-01-01",
            "monthly": "pushed:>2024-01-01"
        }
        query_parts.append(time_filters.get(since, "pushed:>2024-01-01"))
        
        search_url = f"{self.GITHUB_API_BASE}/search/repositories"
        params = {
            "q": " ".join(query_parts),
            "sort": "stars",
            "order": "desc",
            "per_page": limit
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Accept": "application/vnd.github.v3+json"}
                
                # Add GitHub token if available for higher rate limits
                github_token = os.getenv("GITHUB_TOKEN")
                if github_token:
                    headers["Authorization"] = f"token {github_token}"
                
                async with session.get(search_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        repos = []
                        
                        for idx, item in enumerate(data.get("items", [])[:limit]):
                            repos.append({
                                "name": item["full_name"],
                                "url": item["html_url"],
                                "description": item.get("description", ""),
                                "stars": item["stargazers_count"],
                                "forks": item["forks_count"],
                                "language": item.get("language", "Unknown"),
                                "topics": item.get("topics", []),
                                "trending_rank": idx + 1,
                                "updated_at": item.get("updated_at"),
                                "homepage": item.get("homepage", "")
                            })
                        
                        return repos
                    else:
                        print(f"GitHub API error: {response.status}")
                        return self._get_fallback_repos()
                        
        except Exception as e:
            print(f"Error fetching GitHub trending: {e}")
            return self._get_fallback_repos()
    
    def _get_fallback_repos(self) -> List[Dict[str, Any]]:
        """Return fallback trending repos if API fails."""
        return [
            {
                "name": "kubernetes/kubernetes",
                "url": "https://github.com/kubernetes/kubernetes",
                "description": "Production-Grade Container Scheduling and Management",
                "stars": 105000,
                "forks": 38000,
                "language": "Go",
                "topics": ["kubernetes", "containers", "orchestration"],
                "trending_rank": 1
            },
            {
                "name": "docker/compose",
                "url": "https://github.com/docker/compose",
                "description": "Define and run multi-container applications with Docker",
                "stars": 32000,
                "forks": 5000,
                "language": "Go",
                "topics": ["docker", "containers", "devops"],
                "trending_rank": 2
            },
            {
                "name": "hashicorp/terraform",
                "url": "https://github.com/hashicorp/terraform",
                "description": "Infrastructure as Code tool for building cloud infrastructure",
                "stars": 40000,
                "forks": 9000,
                "language": "Go",
                "topics": ["terraform", "infrastructure", "iac"],
                "trending_rank": 3
            },
            {
                "name": "prometheus/prometheus",
                "url": "https://github.com/prometheus/prometheus",
                "description": "The Prometheus monitoring system and time series database",
                "stars": 52000,
                "forks": 8700,
                "language": "Go",
                "topics": ["monitoring", "metrics", "alerting"],
                "trending_rank": 4
            },
            {
                "name": "grafana/grafana",
                "url": "https://github.com/grafana/grafana",
                "description": "Open source analytics and monitoring platform",
                "stars": 60000,
                "forks": 11000,
                "language": "TypeScript",
                "topics": ["grafana", "monitoring", "visualization"],
                "trending_rank": 5
            }
        ]
    
    async def get_repo_details(self, repo_url: str) -> Dict[str, Any]:
        """
        Fetch detailed information about a specific repository.
        
        Args:
            repo_url: Full GitHub repository URL
            
        Returns:
            Detailed repository information
        """
        # Extract owner/repo from URL
        match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
        if not match:
            return {}
        
        owner, repo = match.groups()
        repo = repo.replace(".git", "")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Accept": "application/vnd.github.v3+json"}
                github_token = os.getenv("GITHUB_TOKEN")
                if github_token:
                    headers["Authorization"] = f"token {github_token}"
                
                # Fetch repo info
                repo_url = f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}"
                async with session.get(repo_url, headers=headers) as response:
                    if response.status == 200:
                        repo_data = await response.json()
                    else:
                        return {}
                
                # Fetch README
                readme_url = f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}/readme"
                readme_content = ""
                async with session.get(readme_url, headers=headers) as response:
                    if response.status == 200:
                        readme_data = await response.json()
                        # Decode base64 content
                        import base64
                        readme_content = base64.b64decode(readme_data.get("content", "")).decode("utf-8", errors="ignore")
                
                return {
                    "name": repo_data["full_name"],
                    "url": repo_data["html_url"],
                    "description": repo_data.get("description", ""),
                    "stars": repo_data["stargazers_count"],
                    "forks": repo_data["forks_count"],
                    "language": repo_data.get("language", "Unknown"),
                    "topics": repo_data.get("topics", []),
                    "license": repo_data.get("license", {}).get("name", "Unknown"),
                    "homepage": repo_data.get("homepage", ""),
                    "readme": readme_content[:5000],  # Limit README size
                    "created_at": repo_data.get("created_at"),
                    "updated_at": repo_data.get("updated_at"),
                    "open_issues": repo_data.get("open_issues_count", 0)
                }
                
        except Exception as e:
            print(f"Error fetching repo details: {e}")
            return {}


class AIBlogGenerator:
    """
    AI-powered blog article generator using Google Gemini.
    """
    
    def __init__(self):
        self.model_name = "models/gemini-2.0-flash"
    
    def is_configured(self) -> bool:
        """Check if Gemini AI is properly configured."""
        return GENAI_AVAILABLE and bool(GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-api-key")
    
    async def generate_from_github_repo(
        self,
        repo_info: Dict[str, Any],
        style: str = "tutorial",
        length: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate a blog article about a GitHub repository.
        
        Args:
            repo_info: Repository information dictionary
            style: Article style - "tutorial", "comparison", "news", "deep-dive"
            length: Article length - "short", "medium", "long"
            
        Returns:
            Generated blog article with title, content, metadata
        """
        if not self.is_configured():
            return self._generate_fallback_article(repo_info)
        
        length_guidelines = {
            "short": "around 500-800 words",
            "medium": "around 1000-1500 words",
            "long": "around 2000-3000 words"
        }
        
        style_instructions = {
            "tutorial": "Write as a practical getting-started tutorial with code examples and step-by-step instructions.",
            "comparison": "Compare this tool with alternatives, highlighting when to choose it vs competitors.",
            "news": "Write as a news/announcement article about the project's significance and recent updates.",
            "deep-dive": "Provide an in-depth technical analysis of the architecture, design decisions, and best practices."
        }
        
        prompt = f"""
You are a technical writer for CloudEngineered, a platform for DevOps and cloud engineering professionals.

Write a comprehensive blog article about this GitHub repository:

**Repository:** {repo_info.get('name', 'Unknown')}
**Description:** {repo_info.get('description', 'No description')}
**Stars:** {repo_info.get('stars', 0):,}
**Language:** {repo_info.get('language', 'Unknown')}
**Topics:** {', '.join(repo_info.get('topics', []))}
**Homepage:** {repo_info.get('homepage', 'N/A')}

**README Excerpt:**
{repo_info.get('readme', 'No README available')[:2000]}

**Article Requirements:**
- Style: {style_instructions.get(style, style_instructions['tutorial'])}
- Length: {length_guidelines.get(length, length_guidelines['medium'])}
- Target audience: DevOps engineers, SREs, and cloud architects
- Include practical examples and use cases
- Add a "Key Takeaways" section at the end
- Use markdown formatting with headers, code blocks, and lists

**Output Format:**
Return a JSON object with:
{{
    "title": "Engaging, SEO-friendly title",
    "excerpt": "2-3 sentence summary for preview",
    "content": "Full markdown article content",
    "tags": ["tag1", "tag2", "tag3"],
    "category": "DevOps category",
    "estimated_read_time": "X min read"
}}
"""
        
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            
            # Parse JSON from response
            response_text = response.text
            
            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            article = json.loads(json_text)
            article["status"] = "draft"
            article["source_repo"] = repo_info.get("url", "")
            article["generated_at"] = datetime.utcnow().isoformat()
            
            return article
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            # Return structured content from raw text
            return {
                "title": f"Getting Started with {repo_info.get('name', 'Unknown')}",
                "excerpt": repo_info.get("description", "")[:200],
                "content": response.text if 'response' in dir() else self._generate_fallback_article(repo_info)["content"],
                "tags": repo_info.get("topics", [])[:5],
                "category": "DevOps",
                "status": "draft",
                "estimated_read_time": "5 min read"
            }
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._generate_fallback_article(repo_info)
    
    async def generate_from_topic(
        self,
        topic: str,
        style: str = "tutorial",
        length: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate a blog article from a custom topic.
        
        Args:
            topic: The topic to write about
            style: Article style
            length: Article length
            
        Returns:
            Generated blog article
        """
        if not self.is_configured():
            return self._generate_fallback_topic_article(topic)
        
        length_guidelines = {
            "short": "around 500-800 words",
            "medium": "around 1000-1500 words",
            "long": "around 2000-3000 words"
        }
        
        prompt = f"""
You are a technical writer for CloudEngineered, a platform for DevOps and cloud engineering professionals.

Write a comprehensive blog article about: **{topic}**

**Article Requirements:**
- Length: {length_guidelines.get(length, length_guidelines['medium'])}
- Target audience: DevOps engineers, SREs, and cloud architects
- Include practical examples, code snippets where relevant
- Add a "Key Takeaways" section at the end
- Use markdown formatting with headers, code blocks, and lists
- Be technically accurate and up-to-date

**Output Format:**
Return a JSON object with:
{{
    "title": "Engaging, SEO-friendly title",
    "excerpt": "2-3 sentence summary for preview",
    "content": "Full markdown article content",
    "tags": ["tag1", "tag2", "tag3"],
    "category": "DevOps category",
    "estimated_read_time": "X min read"
}}
"""
        
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            
            response_text = response.text
            
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            article = json.loads(json_text)
            article["status"] = "draft"
            article["generated_at"] = datetime.utcnow().isoformat()
            
            return article
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._generate_fallback_topic_article(topic)
    
    def _generate_fallback_article(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback article when AI is not available."""
        name = repo_info.get("name", "Unknown")
        description = repo_info.get("description", "A powerful open-source tool")
        stars = repo_info.get("stars", 0)
        language = repo_info.get("language", "Unknown")
        topics = repo_info.get("topics", [])
        
        content = f"""# Getting Started with {name}

## Introduction

{name} is a popular open-source project with over {stars:,} GitHub stars. {description}

## Why Use {name}?

With the growing complexity of modern infrastructure, tools like {name} have become essential for DevOps teams. Here's why you should consider it:

- **Community Support**: With {stars:,} stars, it has a vibrant community
- **Active Development**: Built with {language}, it's actively maintained
- **Industry Standard**: Used by leading tech companies worldwide

## Key Features

{name} offers several powerful features:

1. **Scalability** - Designed to handle enterprise workloads
2. **Flexibility** - Highly configurable to meet your needs
3. **Integration** - Works well with existing DevOps tools

## Getting Started

To get started with {name}, visit the [official repository]({repo_info.get('url', '#')}) for detailed installation instructions.

## Key Takeaways

- {name} is a battle-tested solution for {', '.join(topics[:3]) if topics else 'DevOps workflows'}
- Strong community backing ensures long-term support
- Easy integration with existing infrastructure

---

*This article was generated by CloudEngineered. Visit the [GitHub repository]({repo_info.get('url', '#')}) for more information.*
"""
        
        return {
            "title": f"Getting Started with {name}: A Comprehensive Guide",
            "excerpt": f"{description[:200]}...",
            "content": content,
            "tags": topics[:5] if topics else ["devops", "open-source"],
            "category": "DevOps",
            "status": "draft",
            "estimated_read_time": "5 min read",
            "source_repo": repo_info.get("url", "")
        }
    
    def _generate_fallback_topic_article(self, topic: str) -> Dict[str, Any]:
        """Generate fallback article for custom topic."""
        content = f"""# {topic}: A Complete Guide for DevOps Engineers

## Introduction

{topic} is an essential concept for modern DevOps and cloud engineering teams. In this guide, we'll explore the fundamentals and best practices.

## Why {topic} Matters

Understanding {topic} is crucial for:

- Improving operational efficiency
- Reducing deployment risks
- Scaling infrastructure effectively

## Best Practices

Here are key best practices to follow:

1. **Start Small** - Begin with pilot projects
2. **Document Everything** - Maintain clear documentation
3. **Automate** - Reduce manual processes where possible
4. **Monitor** - Implement comprehensive monitoring

## Key Takeaways

- {topic} is essential for modern DevOps workflows
- Proper implementation leads to significant efficiency gains
- Continuous learning and adaptation are key to success

---

*This article was generated by CloudEngineered.*
"""
        
        return {
            "title": f"{topic}: A Complete Guide for DevOps Engineers",
            "excerpt": f"Learn everything you need to know about {topic} in this comprehensive guide.",
            "content": content,
            "tags": ["devops", topic.lower().replace(" ", "-")],
            "category": "DevOps",
            "status": "draft",
            "estimated_read_time": "5 min read"
        }


# Create singleton instances
github_trending_service = GitHubTrendingService()
ai_blog_generator = AIBlogGenerator()
