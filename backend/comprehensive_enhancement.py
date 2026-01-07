from enhance_tools import ToolEnhancer
from web_scraper import WebScraper
from main import SessionLocal, Tool

def comprehensive_tool_enhancement():
    """Enhance all tools with data from GitHub, homepages, and other sources"""
    db = SessionLocal()
    
    try:
        tools = db.query(Tool).all()
        enhancer = ToolEnhancer()
        scraper = WebScraper()
        
        print(f"🚀 Starting comprehensive enhancement of {len(tools)} tools...")
        
        for tool in tools:
            print(f"\n📦 Processing {tool.name}...")
            
            # 1. GitHub Enhancement (README, stats)
            github_info = enhancer.extract_github_info(tool.github_url)
            if github_info:
                print(f"  📚 Fetching GitHub README...")
                readme_content = enhancer.fetch_github_readme(github_info['owner'], github_info['repo'])
                github_stats = enhancer.fetch_github_stats(github_info['owner'], github_info['repo'])
                
                if readme_content:
                    readme_info = enhancer.parse_readme_content(readme_content)
                    print(f"    ✅ Found {len(readme_info.get('features', []))} features in README")
                else:
                    readme_info = {}
                    print(f"    ❌ No README found")
            else:
                readme_info = {}
                github_stats = {}
                print(f"  ❌ No valid GitHub URL")
            
            # 2. Web Scraping Enhancement (homepage, Docker Hub, etc.)
            print(f"  🌐 Scraping web sources...")
            web_data = scraper.enhance_tool_with_web_data(tool.name, tool.homepage_url)
            print(f"    ✅ Found {len(web_data.get('web_features', []))} web features")
            
            # 3. Combine all data sources
            enhanced_description_parts = []
            
            # Start with existing description
            if tool.description and not any(marker in tool.description for marker in ['**GitHub Description**', '**Key Features:**']):
                enhanced_description_parts.append(tool.description)
            
            # Add web description if available and different
            if web_data.get('web_description') and web_data['web_description'] not in str(tool.description):
                enhanced_description_parts.append(f"\n**Web Description:**\n{web_data['web_description']}")
            
            # Add GitHub description
            if github_stats.get('description') and github_stats['description'] not in str(tool.description):
                enhanced_description_parts.append(f"\n**GitHub Description:**\n{github_stats['description']}")
            
            # Combine features from all sources
            all_features = []
            
            # README features
            if readme_info.get('features'):
                all_features.extend(readme_info['features'][:8])
            
            # Web features
            if web_data.get('web_features'):
                # Filter out duplicates and add unique web features
                web_features = [f for f in web_data['web_features'][:5] if f not in all_features]
                all_features.extend(web_features)
            
            # Add features section
            if all_features:
                features_text = "\n**Key Features:**\n"
                for feature in all_features[:12]:  # Limit to 12 total features
                    features_text += f"• {feature}\n"
                enhanced_description_parts.append(features_text)
            
            # Add architecture info from README
            if readme_info.get('architecture'):
                enhanced_description_parts.append(f"\n**Architecture Overview:**\n{readme_info['architecture']}")
            
            # Add installation info
            if readme_info.get('installation'):
                enhanced_description_parts.append(f"\n**Installation:**\n{readme_info['installation']}")
            
            # Add Docker info if available
            if web_data.get('docker_info') and web_data['docker_info']:
                docker_info = web_data['docker_info']
                docker_text = "\n**Docker Information:**\n"
                if docker_info.get('docker_image'):
                    docker_text += f"• Official Image: {docker_info['docker_image']}\n"
                if docker_info.get('docker_pulls'):
                    docker_text += f"• Docker Pulls: {docker_info['docker_pulls']:,}\n"
                enhanced_description_parts.append(docker_text)
            
            # Add package manager info
            if web_data.get('package_info'):
                for pkg_type, pkg_data in web_data['package_info'].items():
                    if pkg_data:
                        pkg_text = f"\n**{pkg_type.upper()} Package:**\n"
                        if pkg_data.get('name'):
                            pkg_text += f"• Package: {pkg_data['name']}\n"
                        if pkg_data.get('version'):
                            pkg_text += f"• Latest Version: {pkg_data['version']}\n"
                        enhanced_description_parts.append(pkg_text)
            
            # Add technical details
            tech_details = []
            if github_stats.get('language'):
                tech_details.append(f"• Primary Language: {github_stats['language']}")
            if github_stats.get('topics'):
                tech_details.append(f"• Topics: {', '.join(github_stats['topics'][:5])}")
            if web_data.get('documentation_links'):
                tech_details.append(f"• Documentation Links: {len(web_data['documentation_links'])} found")
            
            if tech_details:
                enhanced_description_parts.append(f"\n**Technical Details:**\n" + '\n'.join(tech_details))
            
            # Update tool with enhanced data
            tool.description = '\n'.join(enhanced_description_parts)
            
            # Update GitHub stats
            if github_stats.get('stars'):
                tool.github_stars = github_stats['stars']
            if github_stats.get('forks'):
                tool.github_forks = github_stats['forks']
            if github_stats.get('license') and not tool.license:
                tool.license = github_stats['license']
            
            print(f"  ✅ Enhanced {tool.name} with comprehensive data")
        
        db.commit()
        print(f"\n🎉 Successfully enhanced all {len(tools)} tools with comprehensive data!")
        
    except Exception as e:
        print(f"❌ Error during enhancement: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    comprehensive_tool_enhancement()
