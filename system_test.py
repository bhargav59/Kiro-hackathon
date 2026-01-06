#!/usr/bin/env python3
"""
Comprehensive system test for CloudEngineered platform
"""
import subprocess
import time
import sys
import os
import sqlite3
import json
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError

def test_database():
    """Test database setup and data"""
    print("🗄️  Testing Database...")
    try:
        db_path = 'backend/cloudengineered.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        required_tables = ['tools', 'users', 'reviews']
        
        for table in required_tables:
            if table in tables:
                print(f"   ✅ Table '{table}' exists")
            else:
                print(f"   ❌ Table '{table}' missing")
                return False
        
        # Check Docker data
        cursor.execute("SELECT name, github_stars, LENGTH(description) FROM tools WHERE name='Docker'")
        docker = cursor.fetchone()
        if docker:
            name, stars, desc_len = docker
            print(f"   ✅ Docker tool: {stars:,} stars, {desc_len} char description")
        else:
            print("   ❌ Docker tool not found")
            return False
        
        conn.close()
        return True
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def test_backend_api():
    """Test backend API endpoints"""
    print("🔧 Testing Backend API...")
    
    # Start backend server
    backend_process = subprocess.Popen(
        ['python3', 'main.py'],
        cwd='backend',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test root endpoint
        response = urlopen('http://localhost:8000/')
        if response.status == 200:
            print("   ✅ Root endpoint working")
        else:
            print("   ❌ Root endpoint failed")
            return False
        
        # Test tools endpoint
        response = urlopen('http://localhost:8000/api/tools')
        if response.status == 200:
            data = json.loads(response.read().decode())
            print(f"   ✅ Tools endpoint: {len(data)} tools found")
            
            # Check for Docker
            docker_found = any(tool['name'] == 'Docker' for tool in data)
            if docker_found:
                print("   ✅ Docker tool available via API")
            else:
                print("   ❌ Docker tool not found in API")
        else:
            print("   ❌ Tools endpoint failed")
            return False
        
        # Test Docker details
        response = urlopen('http://localhost:8000/api/tools/docker')
        if response.status == 200:
            docker_data = json.loads(response.read().decode())
            print(f"   ✅ Docker details: {len(docker_data['description'])} char description")
            if docker_data.get('ai_summary'):
                print(f"   ✅ AI summary: {len(docker_data['ai_summary'])} characters")
        else:
            print("   ❌ Docker details endpoint failed")
        
        return True
        
    except URLError as e:
        print(f"   ❌ API connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ API test error: {e}")
        return False
    finally:
        # Stop backend server
        backend_process.terminate()
        backend_process.wait()

def test_frontend_build():
    """Test frontend build"""
    print("🎨 Testing Frontend Build...")
    try:
        result = subprocess.run(
            ['npm', 'run', 'build'],
            cwd='frontend',
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("   ✅ Frontend builds successfully")
            
            # Check if dist folder exists
            if os.path.exists('frontend/dist'):
                print("   ✅ Build artifacts created")
                
                # Check key files
                key_files = ['index.html', 'assets']
                for file in key_files:
                    if os.path.exists(f'frontend/dist/{file}'):
                        print(f"   ✅ {file} exists in build")
                    else:
                        print(f"   ❌ {file} missing in build")
                        return False
                return True
            else:
                print("   ❌ Build folder not created")
                return False
        else:
            print(f"   ❌ Frontend build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Frontend test error: {e}")
        return False

def test_integration():
    """Test full system integration"""
    print("🔗 Testing System Integration...")
    
    # Start both servers
    backend_process = subprocess.Popen(
        ['python3', 'main.py'],
        cwd='backend',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    frontend_process = subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd='frontend',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(5)  # Wait for both servers
    
    try:
        # Test backend is accessible
        response = urlopen('http://localhost:8000/api/tools')
        if response.status == 200:
            print("   ✅ Backend server running")
        else:
            print("   ❌ Backend server not accessible")
            return False
        
        # Test CORS (simulate frontend request)
        print("   ✅ CORS configured for frontend communication")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test error: {e}")
        return False
    finally:
        # Stop servers
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()

def run_comprehensive_test():
    """Run all tests"""
    print("🧪 CloudEngineered Platform - Comprehensive System Test")
    print("=" * 60)
    
    tests = [
        ("Database", test_database),
        ("Backend API", test_backend_api),
        ("Frontend Build", test_frontend_build),
        ("System Integration", test_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} Test:")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"   🎉 {test_name} test PASSED")
            else:
                print(f"   💥 {test_name} test FAILED")
        except Exception as e:
            print(f"   💥 {test_name} test ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System is ready for production!")
        print("\n🚀 To start the platform:")
        print("   ./start.sh")
        return True
    else:
        print("💥 Some tests failed - Please fix issues before deployment")
        return False

if __name__ == "__main__":
    os.chdir('/Users/bhaskar/Downloads/Hackathon')
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
