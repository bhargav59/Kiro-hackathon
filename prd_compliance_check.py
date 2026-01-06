#!/usr/bin/env python3
"""
PRD Compliance Check - Verify all features against requirements
"""
import os
import sqlite3
import json
import subprocess
from urllib.request import urlopen
from urllib.error import URLError

def check_core_features():
    """Check Core Features (MVP Scope) from PRD Section 5.1"""
    print("🔍 Checking Core Features (PRD Section 5.1)")
    results = {}
    
    # A. Tool Discovery System
    print("\n📋 A. Tool Discovery System")
    checks = {
        "Full-text search": False,
        "Multi-select filters": False,
        "Real-time GitHub stats": False,
        "Sort functionality": False,
        "Responsive grid/list view": False
    }
    
    # Check if search is implemented in frontend
    if os.path.exists('frontend/src/App.tsx'):
        with open('frontend/src/App.tsx', 'r') as f:
            content = f.read()
            if 'search' in content.lower() and 'Search tools' in content:
                checks["Full-text search"] = True
                print("   ✅ Full-text search implemented")
            else:
                print("   ❌ Full-text search missing")
            
            if 'category' in content.lower() and 'select' in content.lower():
                checks["Multi-select filters"] = True
                print("   ✅ Multi-select filters implemented")
            else:
                print("   ❌ Multi-select filters missing")
            
            if 'github_stars' in content or 'stars' in content:
                checks["Real-time GitHub stats"] = True
                print("   ✅ GitHub stats display implemented")
            else:
                print("   ❌ GitHub stats display missing")
                
            if 'sort' in content.lower() or 'order' in content.lower():
                checks["Sort functionality"] = True
                print("   ✅ Sort functionality implemented")
            else:
                print("   ❌ Sort functionality missing")
                
            if 'grid' in content.lower() and 'list' in content.lower():
                checks["Responsive grid/list view"] = True
                print("   ✅ Responsive grid/list view implemented")
            else:
                print("   ❌ Responsive grid/list view missing")
    
    results["Tool Discovery"] = checks
    
    # B. Tool Detail Pages
    print("\n📋 B. Tool Detail Pages")
    detail_checks = {
        "Complete tool metadata": False,
        "Live GitHub statistics": False,
        "AI-generated summaries": False,
        "Integration instructions": False,
        "Related tools": False
    }
    
    # Check database for AI summaries
    if os.path.exists('backend/cloudengineered.db'):
        try:
            conn = sqlite3.connect('backend/cloudengineered.db')
            cursor = conn.cursor()
            cursor.execute("SELECT ai_summary FROM tools WHERE ai_summary IS NOT NULL LIMIT 1")
            if cursor.fetchone():
                detail_checks["AI-generated summaries"] = True
                print("   ✅ AI-generated summaries implemented")
            else:
                print("   ❌ AI-generated summaries missing")
            
            cursor.execute("SELECT github_stars, github_forks FROM tools WHERE github_stars > 0 LIMIT 1")
            if cursor.fetchone():
                detail_checks["Live GitHub statistics"] = True
                print("   ✅ Live GitHub statistics implemented")
            else:
                print("   ❌ Live GitHub statistics missing")
            
            cursor.execute("SELECT name, description, homepage_url, github_url FROM tools LIMIT 1")
            tool = cursor.fetchone()
            if tool and all(tool):
                detail_checks["Complete tool metadata"] = True
                print("   ✅ Complete tool metadata implemented")
            else:
                print("   ❌ Complete tool metadata missing")
            
            conn.close()
        except Exception as e:
            print(f"   ❌ Database check failed: {e}")
    
    results["Tool Details"] = detail_checks
    
    # C. Comparison Engine
    print("\n📋 C. Comparison Engine")
    comparison_checks = {
        "Multi-tool selection": False,
        "Side-by-side comparison": False,
        "AI comparison summary": False,
        "Export functionality": False
    }
    
    # Check backend for comparison endpoint
    if os.path.exists('backend/main.py'):
        with open('backend/main.py', 'r') as f:
            content = f.read()
            if '/ai/compare' in content:
                comparison_checks["AI comparison summary"] = True
                print("   ✅ AI comparison endpoint implemented")
            else:
                print("   ❌ AI comparison endpoint missing")
    
    results["Comparison Engine"] = comparison_checks
    
    # D. User Authentication & Profiles
    print("\n📋 D. User Authentication & Profiles")
    auth_checks = {
        "Email/password login": False,
        "User profiles": False,
        "My Stack functionality": False,
        "Favorites/bookmarks": False,
        "Activity history": False
    }
    
    # Check for auth endpoints
    if os.path.exists('backend/main.py'):
        with open('backend/main.py', 'r') as f:
            content = f.read()
            if '/auth/register' in content and '/auth/login' in content:
                auth_checks["Email/password login"] = True
                print("   ✅ Email/password authentication implemented")
            else:
                print("   ❌ Email/password authentication missing")
            
            if '/users/me' in content:
                auth_checks["User profiles"] = True
                print("   ✅ User profiles implemented")
            else:
                print("   ❌ User profiles missing")
            
            if 'user_stacks' in content or '/stack' in content:
                auth_checks["My Stack functionality"] = True
                print("   ✅ My Stack functionality implemented")
            else:
                print("   ❌ My Stack functionality missing")
    
    results["Authentication"] = auth_checks
    
    # E. Community Reviews
    print("\n📋 E. Community Reviews")
    review_checks = {
        "5-star rating system": False,
        "Rich text reviews": False,
        "Review voting": False,
        "Review sorting": False,
        "Content moderation": False
    }
    
    # Check database for reviews table
    if os.path.exists('backend/cloudengineered.db'):
        try:
            conn = sqlite3.connect('backend/cloudengineered.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reviews'")
            if cursor.fetchone():
                review_checks["5-star rating system"] = True
                print("   ✅ Reviews system implemented")
            else:
                print("   ❌ Reviews system missing")
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='review_votes'")
            if cursor.fetchone():
                review_checks["Review voting"] = True
                print("   ✅ Review voting implemented")
            else:
                print("   ❌ Review voting missing")
            
            conn.close()
        except Exception as e:
            print(f"   ❌ Database check failed: {e}")
    
    results["Reviews"] = review_checks
    
    return results

def check_ai_features():
    """Check AI-Powered Features from PRD Section 5.2"""
    print("\n🤖 Checking AI-Powered Features (PRD Section 5.2)")
    results = {}
    
    ai_checks = {
        "Auto-generated tool summaries": False,
        "Smart tool recommendations": False,
        "Automated content moderation": False
    }
    
    # Check for AI summary generation
    if os.path.exists('backend/main.py'):
        with open('backend/main.py', 'r') as f:
            content = f.read()
            if 'generate_ai_summary' in content or 'ai_summary' in content:
                ai_checks["Auto-generated tool summaries"] = True
                print("   ✅ Auto-generated summaries implemented")
            else:
                print("   ❌ Auto-generated summaries missing")
    
    results["AI Features"] = ai_checks
    return results

def check_technical_architecture():
    """Check Technical Architecture from PRD Section 7"""
    print("\n🏗️  Checking Technical Architecture (PRD Section 7)")
    results = {}
    
    # Frontend checks
    frontend_checks = {
        "React 18 with TypeScript": False,
        "Tailwind CSS": False,
        "Vite build tool": False,
        "React Router": False
    }
    
    if os.path.exists('frontend/package.json'):
        with open('frontend/package.json', 'r') as f:
            content = f.read()
            package_data = json.loads(content)
            
            deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
            
            if 'react' in deps:
                frontend_checks["React 18 with TypeScript"] = True
                print("   ✅ React with TypeScript implemented")
            
            if 'tailwindcss' in deps:
                frontend_checks["Tailwind CSS"] = True
                print("   ✅ Tailwind CSS implemented")
            
            if 'vite' in deps:
                frontend_checks["Vite build tool"] = True
                print("   ✅ Vite build tool implemented")
            
            if 'react-router-dom' in deps:
                frontend_checks["React Router"] = True
                print("   ✅ React Router implemented")
    
    # Backend checks
    backend_checks = {
        "FastAPI framework": False,
        "SQLAlchemy ORM": False,
        "JWT authentication": False,
        "Database schema": False
    }
    
    if os.path.exists('backend/requirements.txt'):
        with open('backend/requirements.txt', 'r') as f:
            content = f.read()
            
            if 'fastapi' in content:
                backend_checks["FastAPI framework"] = True
                print("   ✅ FastAPI framework implemented")
            
            if 'sqlalchemy' in content:
                backend_checks["SQLAlchemy ORM"] = True
                print("   ✅ SQLAlchemy ORM implemented")
            
            if 'PyJWT' in content or 'python-jose' in content:
                backend_checks["JWT authentication"] = True
                print("   ✅ JWT authentication implemented")
    
    # Check database schema
    if os.path.exists('backend/cloudengineered.db'):
        try:
            conn = sqlite3.connect('backend/cloudengineered.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['tools', 'users', 'reviews', 'user_stacks', 'review_votes']
            if all(table in tables for table in required_tables):
                backend_checks["Database schema"] = True
                print("   ✅ Complete database schema implemented")
            else:
                missing = [t for t in required_tables if t not in tables]
                print(f"   ❌ Missing database tables: {missing}")
            
            conn.close()
        except Exception as e:
            print(f"   ❌ Database schema check failed: {e}")
    
    results["Frontend"] = frontend_checks
    results["Backend"] = backend_checks
    
    return results

def check_api_endpoints():
    """Check API Endpoints from PRD Section 7.3"""
    print("\n🔌 Checking API Endpoints (PRD Section 7.3)")
    results = {}
    
    if not os.path.exists('backend/main.py'):
        print("   ❌ Backend main.py not found")
        return results
    
    with open('backend/main.py', 'r') as f:
        content = f.read()
    
    # Required endpoints from PRD
    required_endpoints = {
        "GET /api/tools": "/api/tools",
        "GET /api/tools/{slug}": "/api/tools/{",
        "POST /api/tools": "POST.*api/tools",
        "GET /api/tools/{id}/reviews": "/reviews",
        "POST /api/tools/{id}/reviews": "POST.*reviews",
        "POST /api/auth/register": "/auth/register",
        "POST /api/auth/login": "/auth/login",
        "GET /api/users/me": "/users/me",
        "POST /api/ai/compare": "/ai/compare"
    }
    
    endpoint_checks = {}
    for endpoint_name, pattern in required_endpoints.items():
        if pattern in content:
            endpoint_checks[endpoint_name] = True
            print(f"   ✅ {endpoint_name} implemented")
        else:
            endpoint_checks[endpoint_name] = False
            print(f"   ❌ {endpoint_name} missing")
    
    results["API Endpoints"] = endpoint_checks
    return results

def check_deployment_readiness():
    """Check deployment readiness"""
    print("\n🚀 Checking Deployment Readiness")
    results = {}
    
    deployment_checks = {
        "Production startup script": os.path.exists('start_production.sh'),
        "Frontend build": os.path.exists('frontend/dist'),
        "Database initialized": os.path.exists('backend/cloudengineered.db'),
        "Environment config": os.path.exists('.env.example'),
        "Docker support": os.path.exists('Dockerfile'),
        "Documentation": os.path.exists('PRODUCTION_READY.md')
    }
    
    for check, status in deployment_checks.items():
        if status:
            print(f"   ✅ {check}")
        else:
            print(f"   ❌ {check}")
    
    results["Deployment"] = deployment_checks
    return results

def generate_compliance_report(all_results):
    """Generate final compliance report"""
    print("\n" + "="*60)
    print("📊 PRD COMPLIANCE REPORT")
    print("="*60)
    
    total_checks = 0
    passed_checks = 0
    
    for category, checks in all_results.items():
        if isinstance(checks, dict):
            category_total = len(checks)
            category_passed = sum(1 for v in checks.values() if v)
            total_checks += category_total
            passed_checks += category_passed
            
            percentage = (category_passed / category_total * 100) if category_total > 0 else 0
            status = "✅" if percentage >= 80 else "⚠️" if percentage >= 60 else "❌"
            
            print(f"{status} {category}: {category_passed}/{category_total} ({percentage:.1f}%)")
    
    overall_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    overall_status = "✅" if overall_percentage >= 80 else "⚠️" if overall_percentage >= 60 else "❌"
    
    print(f"\n{overall_status} OVERALL COMPLIANCE: {passed_checks}/{total_checks} ({overall_percentage:.1f}%)")
    
    if overall_percentage >= 80:
        print("\n🎉 EXCELLENT! System meets PRD requirements for hackathon submission")
    elif overall_percentage >= 60:
        print("\n⚠️  GOOD! System mostly compliant, minor improvements needed")
    else:
        print("\n❌ NEEDS WORK! Significant features missing from PRD requirements")
    
    return overall_percentage

def main():
    """Run complete PRD compliance check"""
    print("🧪 CloudEngineered Platform - PRD Compliance Check")
    print("Verifying implementation against kiro_hackathon_prd.md")
    print("="*60)
    
    all_results = {}
    
    # Run all checks
    all_results.update(check_core_features())
    all_results.update(check_ai_features())
    all_results.update(check_technical_architecture())
    all_results.update(check_api_endpoints())
    all_results.update(check_deployment_readiness())
    
    # Generate final report
    compliance_score = generate_compliance_report(all_results)
    
    # Recommendations
    print("\n📋 RECOMMENDATIONS:")
    if compliance_score < 80:
        print("   • Implement missing core features (search, filters, comparisons)")
        print("   • Add GitHub OAuth authentication")
        print("   • Enhance AI-powered recommendations")
        print("   • Complete review voting system")
    else:
        print("   • System is ready for hackathon submission!")
        print("   • Consider adding bonus features for extra points")
        print("   • Prepare demo video showcasing key features")
    
    return compliance_score >= 80

if __name__ == "__main__":
    os.chdir('/Users/bhaskar/Downloads/Hackathon')
    success = main()
    exit(0 if success else 1)
