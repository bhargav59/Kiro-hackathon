import requests
import base64
import re
from typing import Dict, Optional
from main import SessionLocal, Tool

class ToolEnhancer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CloudEngineered-Platform/1.0'
        })

    def extract_github_info(self, github_url: str) -> Dict:
        """Extract owner and repo from GitHub URL"""
        if not github_url or "github.com" not in github_url:
            return {}
        
        try:
            # Extract owner/repo from GitHub URL
            parts = github_url.replace("https://github.com/", "").split("/")
            if len(parts) >= 2:
                return {"owner": parts[0], "repo": parts[1]}
        except Exception as e:
            print(f"Error extracting GitHub info: {e}")
        
        return {}

    def fetch_github_readme(self, owner: str, repo: str) -> Optional[str]:
        """Fetch README content from GitHub API"""
        try:
            # Try different README file names
            readme_files = ['README.md', 'readme.md', 'README.rst', 'README.txt', 'README']
            
            for readme_file in readme_files:
                url = f"https://api.github.com/repos/{owner}/{repo}/contents/{readme_file}"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('content'):
                        # Decode base64 content
                        content = base64.b64decode(data['content']).decode('utf-8')
                        return content
            
            return None
        except Exception as e:
            print(f"Error fetching README for {owner}/{repo}: {e}")
            return None

    def parse_readme_content(self, readme_content: str) -> Dict:
        """Parse README content to extract structured information"""
        if not readme_content:
            return {}

        parsed_info = {
            'features': [],
            'installation': '',
            'usage': '',
            'architecture': '',
            'requirements': '',
            'examples': []
        }

        # Split content into sections
        sections = re.split(r'\n#+\s+', readme_content)
        
        for section in sections:
            lines = section.split('\n')
            if not lines:
                continue
                
            header = lines[0].lower().strip()
            content = '\n'.join(lines[1:]).strip()
            
            # Extract features
            if any(keyword in header for keyword in ['feature', 'capabilit', 'highlight', 'what']):
                # Extract bullet points
                features = re.findall(r'[-*+]\s+(.+)', content)
                parsed_info['features'].extend(features)
            
            # Extract installation info
            elif any(keyword in header for keyword in ['install', 'setup', 'getting started', 'quick start']):
                parsed_info['installation'] = content[:500]  # Limit length
            
            # Extract usage info
            elif any(keyword in header for keyword in ['usage', 'example', 'how to', 'tutorial']):
                parsed_info['usage'] = content[:500]
            
            # Extract architecture info
            elif any(keyword in header for keyword in ['architect', 'design', 'overview', 'concept']):
                parsed_info['architecture'] = content[:500]
            
            # Extract requirements
            elif any(keyword in header for keyword in ['requirement', 'prerequisite', 'depend']):
                parsed_info['requirements'] = content[:300]

        return parsed_info

    def fetch_github_stats(self, owner: str, repo: str) -> Dict:
        """Fetch additional GitHub statistics"""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'watchers': data.get('watchers_count', 0),
                    'issues': data.get('open_issues_count', 0),
                    'language': data.get('language', ''),
                    'topics': data.get('topics', []),
                    'description': data.get('description', ''),
                    'created_at': data.get('created_at', ''),
                    'updated_at': data.get('updated_at', ''),
                    'size': data.get('size', 0),
                    'license': data.get('license', {}).get('name', '') if data.get('license') else ''
                }
        except Exception as e:
            print(f"Error fetching GitHub stats for {owner}/{repo}: {e}")
        
        return {}

    def enhance_tool_description(self, tool: Tool, readme_info: Dict, github_stats: Dict) -> str:
        """Create enhanced description combining existing info with README data"""
        enhanced_parts = []
        
        # Start with existing description
        if tool.description:
            enhanced_parts.append(tool.description)
        
        # Add GitHub description if different
        if github_stats.get('description') and github_stats['description'] not in tool.description:
            enhanced_parts.append(f"\n**GitHub Description:**\n{github_stats['description']}")
        
        # Add features from README
        if readme_info.get('features'):
            features_text = "\n**Key Features:**\n"
            for feature in readme_info['features'][:10]:  # Limit to 10 features
                features_text += f"• {feature}\n"
            enhanced_parts.append(features_text)
        
        # Add architecture info
        if readme_info.get('architecture'):
            enhanced_parts.append(f"\n**Architecture Overview:**\n{readme_info['architecture']}")
        
        # Add installation info
        if readme_info.get('installation'):
            enhanced_parts.append(f"\n**Installation:**\n{readme_info['installation']}")
        
        # Add usage info
        if readme_info.get('usage'):
            enhanced_parts.append(f"\n**Usage:**\n{readme_info['usage']}")
        
        # Add technical details
        if github_stats.get('language') or github_stats.get('topics'):
            tech_info = "\n**Technical Details:**\n"
            if github_stats.get('language'):
                tech_info += f"• Primary Language: {github_stats['language']}\n"
            if github_stats.get('topics'):
                tech_info += f"• Topics: {', '.join(github_stats['topics'][:5])}\n"
            enhanced_parts.append(tech_info)
        
        return '\n'.join(enhanced_parts)

    def enhance_all_tools(self):
        """Enhance all tools in the database with GitHub README data"""
        db = SessionLocal()
        
        try:
            tools = db.query(Tool).all()
            print(f"Enhancing {len(tools)} tools with GitHub data...")
            
            for tool in tools:
                print(f"Processing {tool.name}...")
                
                # Extract GitHub info
                github_info = self.extract_github_info(tool.github_url)
                if not github_info:
                    print(f"  No valid GitHub URL for {tool.name}")
                    continue
                
                # Fetch README and stats
                readme_content = self.fetch_github_readme(github_info['owner'], github_info['repo'])
                github_stats = self.fetch_github_stats(github_info['owner'], github_info['repo'])
                
                if readme_content:
                    readme_info = self.parse_readme_content(readme_content)
                    
                    # Update tool description
                    enhanced_description = self.enhance_tool_description(tool, readme_info, github_stats)
                    tool.description = enhanced_description
                    
                    # Update GitHub stats
                    if github_stats.get('stars'):
                        tool.github_stars = github_stats['stars']
                    if github_stats.get('forks'):
                        tool.github_forks = github_stats['forks']
                    if github_stats.get('license') and not tool.license:
                        tool.license = github_stats['license']
                    
                    print(f"  ✅ Enhanced {tool.name} with README data")
                else:
                    print(f"  ❌ Could not fetch README for {tool.name}")
            
            db.commit()
            print("✅ All tools enhanced successfully!")
            
        except Exception as e:
            print(f"Error enhancing tools: {e}")
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    enhancer = ToolEnhancer()
    enhancer.enhance_all_tools()
