#!/usr/bin/env python3
"""
Diagnostic script to check Genesis Engine setup
Run this on colleague's machine to identify issues
"""

import sys
import os
import subprocess
from pathlib import Path

def check_env():
    """Check if .env file exists and has required variables"""
    print("\n🔍 Checking .env configuration...")
    
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    required_vars = [
        "TIGER_SERVICE_ID",
        "TIGER_DB_HOST",
        "TIGER_DB_USER",
        "TIGER_DB_PASSWORD",
        "GEMINI_API_KEY"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("   Make sure to: source venv/bin/activate")
        return False
    
    print("✅ .env file configured")
    print(f"   TIGER_SERVICE_ID: {os.getenv('TIGER_SERVICE_ID')}")
    print(f"   TIGER_DB_HOST: {os.getenv('TIGER_DB_HOST')}")
    return True


def check_tiger_cli():
    """Check if Tiger CLI is installed and authenticated"""
    print("\n🔍 Checking Tiger CLI...")
    
    try:
        result = subprocess.run(
            ["tiger", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Tiger CLI installed: {result.stdout.strip()}")
        else:
            print("❌ Tiger CLI not working properly")
            return False
    except FileNotFoundError:
        print("❌ Tiger CLI not installed")
        print("   Install: https://docs.tigergraph.com/cloud/")
        return False
    except Exception as e:
        print(f"❌ Error checking Tiger CLI: {e}")
        return False
    
    # Check authentication
    try:
        result = subprocess.run(
            ["tiger", "service", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Tiger CLI authenticated")
            return True
        else:
            print("❌ Tiger CLI not authenticated")
            print("   Run: tiger auth login")
            return False
    except Exception as e:
        print(f"❌ Error checking Tiger authentication: {e}")
        return False


def check_database():
    """Check database connection"""
    print("\n🔍 Checking database connection...")
    
    try:
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def check_schema():
    """Check if database schema is up to date"""
    print("\n🔍 Checking database schema...")
    
    try:
        from app.database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        
        # Check tables exist
        tables = inspector.get_table_names()
        required_tables = ["projects", "blueprints", "analyses"]
        
        for table in required_tables:
            if table not in tables:
                print(f"❌ Table '{table}' does not exist")
                return False
        
        print("✅ All required tables exist")
        
        # Check blueprint columns
        blueprint_columns = [c['name'] for c in inspector.get_columns('blueprints')]
        if 'mermaid_diagram' not in blueprint_columns:
            print("⚠️  'mermaid_diagram' column missing from blueprints table")
            print("   Run: ALTER TABLE blueprints ADD COLUMN mermaid_diagram TEXT;")
            return False
        
        # Check analysis columns
        analysis_columns = [c['name'] for c in inspector.get_columns('analyses')]
        if 'agent_type' not in analysis_columns:
            print("⚠️  'agent_type' column missing from analyses table")
            print("   Run: ALTER TABLE analyses ADD COLUMN agent_type VARCHAR(20);")
            return False
        
        print("✅ Database schema is up to date")
        return True
    except Exception as e:
        print(f"❌ Schema check failed: {e}")
        return False


def check_forks():
    """Check if can access database forks"""
    print("\n🔍 Checking database fork access...")
    
    service_id = os.getenv('TIGER_SERVICE_ID')
    if not service_id:
        print("❌ TIGER_SERVICE_ID not set")
        return False
    
    try:
        result = subprocess.run(
            ["tiger", "service", "fork", "list", service_id],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            forks = result.stdout
            if "project_" in forks:
                print("✅ Can access database forks")
                print(f"   Found forks in service {service_id}")
                return True
            else:
                print("⚠️  No project forks found")
                print("   This is normal if no projects have been generated yet")
                return True
        else:
            print(f"❌ Failed to list forks: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking forks: {e}")
        return False


def main():
    print("=" * 70)
    print("🏗️  The Genesis Engine - Diagnostic Tool")
    print("=" * 70)
    
    # Change to backend directory
    os.chdir(Path(__file__).parent)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
    
    checks = [
        ("Environment Configuration", check_env),
        ("Tiger CLI", check_tiger_cli),
        ("Database Connection", check_database),
        ("Database Schema", check_schema),
        ("Database Forks", check_forks),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ {name} check failed with error: {e}")
            results[name] = False
    
    print("\n" + "=" * 70)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 All checks passed! System should be working.")
        print("\nNext steps:")
        print("1. Run backend: uvicorn app.main:app --reload --port 8000")
        print("2. Run frontend: cd ../frontend && npm run dev")
        print("3. Generate a project to test")
    else:
        print("\n⚠️  Some checks failed. Fix the issues above.")
        print("\nCommon fixes:")
        print("• Tiger CLI: Run 'tiger auth login'")
        print("• Schema: Run the ALTER TABLE commands shown above")
        print("• .env: Make sure file exists with all required variables")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

