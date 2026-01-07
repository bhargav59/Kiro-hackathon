import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_homepage(self, url: str) -> Dict:
        """Scrape tool homepage for additional information"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract meta information
            info = {
                'title': '',
                'description': '',
                'features': [],
                'keywords': []
            }
            
            # Get title
            title_tag = soup.find('title')
            if title_tag:
                info['title'] = title_tag.get_text().strip()
            
            # Get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                info['description'] = meta_desc.get('content', '').strip()
            
            # Get meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                keywords = meta_keywords.get('content', '').split(',')
                info['keywords'] = [k.strip() for k in keywords if k.strip()]
            
            # Extract features from common patterns
            feature_patterns = [
                'h2', 'h3', 'h4',  # Headers that might contain features
                '.feature', '.benefit', '.capability',  # Common CSS classes
                '[class*="feature"]', '[class*="benefit"]'  # Partial class matches
            ]
            
            features = []
            for pattern in feature_patterns:
                elements = soup.select(pattern)
                for element in elements[:10]:  # Limit to avoid too much data
                    text = element.get_text().strip()
                    if text and len(text) < 200:  # Reasonable length
                        features.append(text)
            
            info['features'] = features[:15]  # Limit features
            
            return info
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {}

    def extract_documentation_links(self, homepage_url: str) -> List[str]:
        """Extract documentation links from homepage"""
        try:
            response = self.session.get(homepage_url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            doc_links = []
            
            # Look for documentation links
            doc_keywords = ['docs', 'documentation', 'guide', 'tutorial', 'manual', 'api']
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text().lower()
                
                if any(keyword in text for keyword in doc_keywords):
                    full_url = urljoin(homepage_url, href)
                    doc_links.append(full_url)
            
            return doc_links[:5]  # Limit to 5 documentation links
            
        except Exception as e:
            print(f"Error extracting doc links from {homepage_url}: {e}")
            return []

    def scrape_docker_hub(self, tool_name: str) -> Dict:
        """Scrape Docker Hub for container information"""
        try:
            # Search for official images
            search_url = f"https://hub.docker.com/v2/search/repositories/?query={tool_name.lower()}&page_size=5"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                for result in results:
                    if result.get('is_official') or tool_name.lower() in result.get('name', '').lower():
                        return {
                            'docker_image': result.get('name'),
                            'docker_description': result.get('short_description'),
                            'docker_pulls': result.get('pull_count', 0),
                            'docker_stars': result.get('star_count', 0)
                        }
            
            return {}
            
        except Exception as e:
            print(f"Error scraping Docker Hub for {tool_name}: {e}")
            return {}

    def scrape_package_managers(self, tool_name: str) -> Dict:
        """Scrape package manager information"""
        package_info = {}
        
        # NPM
        try:
            npm_url = f"https://registry.npmjs.org/{tool_name.lower()}"
            response = self.session.get(npm_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                package_info['npm'] = {
                    'name': data.get('name'),
                    'description': data.get('description'),
                    'version': data.get('dist-tags', {}).get('latest'),
                    'downloads': data.get('downloads', {}).get('weekly', 0)
                }
        except:
            pass
        
        # PyPI
        try:
            pypi_url = f"https://pypi.org/pypi/{tool_name.lower()}/json"
            response = self.session.get(pypi_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                info = data.get('info', {})
                package_info['pypi'] = {
                    'name': info.get('name'),
                    'description': info.get('summary'),
                    'version': info.get('version'),
                    'author': info.get('author')
                }
        except:
            pass
        
        return package_info

    def enhance_tool_with_web_data(self, tool_name: str, homepage_url: str) -> Dict:
        """Combine all web scraping results"""
        enhanced_data = {
            'web_features': [],
            'web_description': '',
            'docker_info': {},
            'package_info': {},
            'documentation_links': []
        }
        
        # Scrape homepage
        if homepage_url:
            homepage_data = self.scrape_homepage(homepage_url)
            enhanced_data['web_features'] = homepage_data.get('features', [])
            enhanced_data['web_description'] = homepage_data.get('description', '')
            enhanced_data['documentation_links'] = self.extract_documentation_links(homepage_url)
        
        # Scrape Docker Hub
        enhanced_data['docker_info'] = self.scrape_docker_hub(tool_name)
        
        # Scrape package managers
        enhanced_data['package_info'] = self.scrape_package_managers(tool_name)
        
        return enhanced_data

if __name__ == "__main__":
    scraper = WebScraper()
    
    # Test with a tool
    result = scraper.enhance_tool_with_web_data("Docker", "https://www.docker.com")
    print("Enhanced data:", result)
