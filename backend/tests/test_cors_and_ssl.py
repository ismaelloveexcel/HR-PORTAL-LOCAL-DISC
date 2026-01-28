"""Test CORS and SSL configuration changes."""

import sys
from pathlib import Path

# Add parent directory to path for imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))


def test_cors_configuration_in_code():
    """Test that CORS middleware code uses correct configuration."""
    # Read the main.py file and check the CORS configuration
    main_py = ROOT / "app" / "main.py"
    content = main_py.read_text()
    
    # Check that allow_origins uses settings.get_allowed_origins_list()
    assert "allow_origins=settings.get_allowed_origins_list()" in content, \
        "CORS middleware should use settings.get_allowed_origins_list()"
    
    # Check that allow_methods is restricted
    assert 'allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]' in content, \
        "CORS middleware should restrict methods to GET, POST, PUT, DELETE, PATCH"
    
    # Check that allow_headers is restricted
    assert 'allow_headers=["Content-Type", "Authorization"]' in content, \
        "CORS middleware should restrict headers to Content-Type and Authorization"
    
    # Make sure we're not using wildcards
    lines = content.split('\n')
    cors_section = []
    in_cors = False
    for line in lines:
        if "CORSMiddleware" in line:
            in_cors = True
        if in_cors:
            cors_section.append(line)
            if ")" in line and in_cors:
                break
    
    cors_text = '\n'.join(cors_section)
    assert 'allow_origins=["*"]' not in cors_text, \
        "CORS should not use wildcard for origins"
    assert 'allow_methods=["*"]' not in cors_text, \
        "CORS should not use wildcard for methods"
    assert 'allow_headers=["*"]' not in cors_text, \
        "CORS should not use wildcard for headers"
    
    print("✓ CORS configuration in main.py is correct")


def test_ssl_configuration_in_database():
    """Test that SSL configuration is properly handled in database.py."""
    database_py = ROOT / "app" / "database.py"
    content = database_py.read_text()
    
    # Check that the utility function is imported and used
    assert 'from app.core.db_utils import clean_database_url_for_asyncpg' in content, \
        "Should import clean_database_url_for_asyncpg utility"
    
    assert 'db_url, ssl_required = clean_database_url_for_asyncpg' in content, \
        "Should use utility function to clean URL and detect SSL"
    
    # Check that SSL connect_args are passed when SSL is required
    assert 'connect_args={"ssl": "require"}' in content, \
        "Should pass SSL connect_args to create_async_engine"
    
    # Check that conditional engine creation exists
    assert 'if ssl_required:' in content, \
        "Should conditionally create engine based on SSL requirement"
    
    print("✓ SSL configuration in database.py is correct")


def test_ssl_configuration_in_alembic():
    """Test that SSL configuration is properly handled in alembic/env.py."""
    env_py = ROOT / "alembic" / "env.py"
    content = env_py.read_text()
    
    # Check that the utility function is imported and used
    assert 'from app.core.db_utils import clean_database_url_for_asyncpg' in content, \
        "Should import clean_database_url_for_asyncpg utility"
    
    assert 'db_url, ssl_required = clean_database_url_for_asyncpg' in content, \
        "Should use utility function to clean URL and detect SSL"
    
    # Check that SSL connect_args are prepared when SSL is required
    assert 'connect_args = {"ssl": "require"}' in content, \
        "Should prepare SSL connect_args"
    
    # Check that conditional connect_args creation exists
    assert 'if ssl_required:' in content, \
        "Should conditionally set connect_args based on SSL requirement"
    
    # Check that connect_args are passed to async_engine_from_config
    assert 'connect_args=connect_args' in content, \
        "Should pass connect_args to async_engine_from_config"
    
    print("✓ SSL configuration in alembic/env.py is correct")


def test_url_cleaning():
    """Test that SSL parameters are properly removed from URLs."""
    import sys
    sys.path.insert(0, str(ROOT))
    from app.core.db_utils import clean_database_url_for_asyncpg
    
    # Test various URL formats including edge cases
    test_cases = [
        ("postgresql://user:pass@host:5432/db?sslmode=require", 
         "postgresql+asyncpg://user:pass@host:5432/db", True),
        ("postgresql://user:pass@host:5432/db?ssl=require",
         "postgresql+asyncpg://user:pass@host:5432/db", True),
        ("postgresql://user:pass@host:5432/db?other=param&sslmode=require",
         "postgresql+asyncpg://user:pass@host:5432/db?other=param", True),
        ("postgresql://user:pass@host:5432/db?sslmode=require&other=param",
         "postgresql+asyncpg://user:pass@host:5432/db?other=param", True),
        ("postgresql://user:pass@host:5432/db?p1=v1&ssl=require&p2=v2",
         "postgresql+asyncpg://user:pass@host:5432/db?p1=v1&p2=v2", True),
        ("postgresql://user:pass@host:5432/db",
         "postgresql+asyncpg://user:pass@host:5432/db", False),
    ]
    
    for original, expected_url, expected_ssl in test_cases:
        cleaned_url, ssl_required = clean_database_url_for_asyncpg(original)
        assert cleaned_url == expected_url, f"URL cleaning failed: {original} -> {cleaned_url} (expected {expected_url})"
        assert ssl_required == expected_ssl, f"SSL detection failed: {original} -> {ssl_required} (expected {expected_ssl})"
    
    print("✓ URL cleaning logic is correct")


def test_ssl_detection_logic():
    """Test that SSL detection logic works correctly."""
    import sys
    sys.path.insert(0, str(ROOT))
    from app.core.db_utils import clean_database_url_for_asyncpg
    
    # Test with SSL required
    test_url_with_ssl = "postgresql://user:pass@host:5432/db?sslmode=require"
    _, ssl_detected = clean_database_url_for_asyncpg(test_url_with_ssl)
    assert ssl_detected, "SSL should be detected in URL with sslmode=require"
    
    test_url_with_ssl2 = "postgresql://user:pass@host:5432/db?ssl=require"
    _, ssl_detected = clean_database_url_for_asyncpg(test_url_with_ssl2)
    assert ssl_detected, "SSL should be detected in URL with ssl=require"
    
    # Test without SSL
    test_url_no_ssl = "postgresql://user:pass@host:5432/db"
    _, ssl_detected = clean_database_url_for_asyncpg(test_url_no_ssl)
    assert not ssl_detected, "SSL should not be detected in URL without SSL params"
    
    print("✓ SSL detection logic is correct")


if __name__ == "__main__":
    test_cors_configuration_in_code()
    test_ssl_configuration_in_database()
    test_ssl_configuration_in_alembic()
    test_ssl_detection_logic()
    test_url_cleaning()
    print("\n✅ All tests passed!")
