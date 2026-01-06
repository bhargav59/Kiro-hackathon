#!/usr/bin/env python3
"""
Quick system readiness check
"""
import os
import sqlite3
import json

def check_project_structure():
    """Check if all required files exist"""
    print("📁 Checking project structure...")
    
    required_files = [
        'README.md',
        'backend/main.py',
        'backend/init_db.py',
        'backend/simple_seed.py',
        'frontend/package.json',
        'frontend/src/App.tsx',
        'start_production.sh'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file}")
            missing.append(file)
    
    return len(missing) == 0

def check_database():
    """Check database and data"""
    print("🗄️  Checking database...")
    
    db_path = 'backend/cloudengineered.db'
    if not os.path.exists(db_path):
        print("   ❌ Database file missing")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check Docker tool
        cursor.execute("SELECT name, github_stars, LENGTH(description), LENGTH(ai_summary) FROM tools WHERE name='Docker'")
        docker = cursor.fetchone()
        
        if docker:
            name, stars, desc_len, summary_len = docker
            print(f"   ✅ Docker tool: {stars:,} stars")
            print(f"   ✅ Description: {desc_len} characters")
            print(f"   ✅ AI Summary: {summary_len} characters")
            
            # Check if enhanced
            if desc_len > 1000 and summary_len > 1000:
                print("   ✅ Docker tool is enhanced with comprehensive details")
                return True
            else:
                print("   ❌ Docker tool needs enhancement")
                return False
        else:
            print("   ❌ Docker tool not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    finally:
        conn.close()

def check_frontend():
    """Check frontend build"""
    print("🎨 Checking frontend...")
    
    if os.path.exists('frontend/dist'):
        print("   ✅ Build directory exists")
        
        if os.path.exists('frontend/dist/index.html'):
            print("   ✅ Built index.html exists")
            return True
        else:
            print("   ❌ Built index.html missing")
            return False
    else:
        print("   ❌ Build directory missing")
        return False

def main():
    """Run all checks"""
    print("🧪 CloudEngineered Platform - Readiness Check")
    print("=" * 50)
    
    checks = [
        ("Project Structure", check_project_structure),
        ("Database & Data", check_database),
        ("Frontend Build", check_frontend)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 50)
    print("📊 READINESS SUMMARY:")
    print("=" * 50)
    
    passed = 0
    for name, result in results:
        status = "✅ READY" if result else "❌ NOT READY"
        print(f"   {name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 SYSTEM IS READY FOR PRODUCTION!")
        print("\n🚀 To start the platform:")
        print("   ./start_production.sh")
        print("\n📋 Manual testing checklist:")
        print("   • Visit http://localhost:3000")
        print("   • Browse tools catalog")
        print("   • View Docker tool details")
        print("   • Check enhanced description and AI summary")
        print("   • Test user registration and login")
        return True
    else:
        print("\n💥 System needs fixes before deployment")
        print("\n🔧 To fix issues:")
        print("   • Run: cd backend && python3 init_db.py && python3 simple_seed.py")
        print("   • Run: cd frontend && npm run build")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
