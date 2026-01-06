import asyncio
import aiohttp
from datetime import datetime
from sqlalchemy.orm import Session
from main import SessionLocal, Tool, fetch_github_stats

async def update_github_stats():
    """Background task to update GitHub statistics for all tools"""
    print("Starting GitHub stats update...")
    
    db = SessionLocal()
    try:
        tools = db.query(Tool).filter(Tool.github_url.isnot(None)).all()
        
        for tool in tools:
            print(f"Updating stats for {tool.name}...")
            try:
                stats = await fetch_github_stats(tool.github_url)
                
                tool.github_stars = stats["stars"]
                tool.github_forks = stats["forks"]
                if stats["last_commit"]:
                    tool.last_commit_date = datetime.fromisoformat(stats["last_commit"].replace("Z", "+00:00"))
                tool.updated_at = datetime.utcnow()
                
                db.commit()
                print(f"Updated {tool.name}: {stats['stars']} stars, {stats['forks']} forks")
                
                # Rate limiting - GitHub API allows 60 requests per hour for unauthenticated requests
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Error updating {tool.name}: {e}")
                continue
                
    except Exception as e:
        print(f"Error in update task: {e}")
    finally:
        db.close()
    
    print("GitHub stats update completed!")

if __name__ == "__main__":
    asyncio.run(update_github_stats())
