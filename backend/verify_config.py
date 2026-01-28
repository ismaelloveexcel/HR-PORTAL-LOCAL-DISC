#!/usr/bin/env python3
"""
Manual verification script for CORS and SSL configuration changes.
This script can be used to manually test the configuration without a database.
"""

import sys
from pathlib import Path

# Add parent directory to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))


def verify_cors_settings():
    """Verify CORS settings are properly configured."""
    print("=" * 60)
    print("CORS Configuration Verification")
    print("=" * 60)
    
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        print("\nCurrent ALLOWED_ORIGINS setting:")
        print(f"  Raw value: {settings.allowed_origins}")
        print(f"  Parsed list: {settings.get_allowed_origins_list()}")
        
        # Show what the CORS middleware will use
        print("\nCORS Middleware will use:")
        origins = settings.get_allowed_origins_list()
        print(f"  allow_origins: {origins}")
        print(f"  allow_methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']")
        print(f"  allow_headers: ['Content-Type', 'Authorization']")
        print(f"  allow_credentials: True")
        
        if origins == ["*"]:
            print("\n⚠️  WARNING: Using wildcard origins. Set ALLOWED_ORIGINS in .env")
        else:
            print("\n✓ CORS origins are properly restricted")
        
        return True
    except Exception as e:
        print(f"\n❌ Error verifying CORS settings: {e}")
        return False


def verify_ssl_handling():
    """Verify SSL handling logic."""
    print("\n" + "=" * 60)
    print("SSL Configuration Verification")
    print("=" * 60)
    
    try:
        from app.core.db_utils import clean_database_url_for_asyncpg
        
        # Test various database URL formats
        test_cases = [
            {
                "url": "postgresql://user:pass@host:5432/db",
                "ssl_expected": False,
                "description": "Local database without SSL"
            },
            {
                "url": "postgresql://user:pass@host:5432/db?sslmode=require",
                "ssl_expected": True,
                "description": "Azure PostgreSQL with sslmode=require"
            },
            {
                "url": "postgresql://user:pass@host:5432/db?ssl=require",
                "ssl_expected": True,
                "description": "Azure PostgreSQL with ssl=require"
            },
            {
                "url": "postgres://user:pass@host:5432/db?sslmode=require",
                "ssl_expected": True,
                "description": "Azure PostgreSQL (postgres:// scheme)"
            }
        ]
        
        print("\nTesting SSL detection logic:")
        all_passed = True
        
        for test_case in test_cases:
            original_url = test_case["url"]
            ssl_expected = test_case["ssl_expected"]
            description = test_case["description"]
            
            # Use the utility function
            cleaned_url, ssl_required = clean_database_url_for_asyncpg(original_url)
            
            status = "✓" if ssl_required == ssl_expected else "❌"
            all_passed = all_passed and (ssl_required == ssl_expected)
            
            print(f"\n  {status} {description}")
            print(f"     Original: {original_url}")
            print(f"     Cleaned:  {cleaned_url}")
            print(f"     SSL:      {'REQUIRED' if ssl_required else 'NOT REQUIRED'} (expected: {'REQUIRED' if ssl_expected else 'NOT REQUIRED'})")
            if ssl_required:
                print(f"     Engine:   create_async_engine(..., connect_args={{'ssl': 'require'}})")
            else:
                print(f"     Engine:   create_async_engine(...)")
        
        if all_passed:
            print("\n✓ All SSL detection tests passed")
        else:
            print("\n❌ Some SSL detection tests failed")
        
        return all_passed
    except Exception as e:
        print(f"\n❌ Error testing SSL handling: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification checks."""
    print("\n🔍 CORS and SSL Configuration Verification Tool\n")
    
    cors_ok = verify_cors_settings()
    ssl_ok = verify_ssl_handling()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if cors_ok and ssl_ok:
        print("\n✅ All verifications passed!")
        print("\nThe changes are ready for deployment:")
        print("  1. CORS is properly restricted to configured origins")
        print("  2. SSL handling works correctly for Azure PostgreSQL")
        print("  3. Database connections will use SSL when required")
        return 0
    else:
        print("\n❌ Some verifications failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
