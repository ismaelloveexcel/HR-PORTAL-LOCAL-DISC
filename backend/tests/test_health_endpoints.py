"""Test health endpoints and version tracking functionality.

These tests validate code structure and patterns without requiring
all dependencies to be installed. They can run in CI/CD environments
where pytest and FastAPI may not be available.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))


def test_health_ping_endpoint_structure():
    """Test that /api/health/ping returns expected structure with version info."""
    # Read the health.py file to verify the endpoint structure
    health_py = ROOT / "app" / "routers" / "health.py"
    content = health_py.read_text()
    
    # Verify ping endpoint returns version info
    assert 'version_info = settings.get_version_info()' in content, \
        "Ping endpoint should get version info from settings"
    
    assert '**version_info' in content, \
        "Ping endpoint should spread version_info into response"
    
    # Verify it imports get_settings
    assert 'from app.core.config import get_settings' in content, \
        "Health endpoints should import get_settings"
    
    print("✓ Health ping endpoint has correct structure for version tracking")


def test_health_revision_endpoint_structure():
    """Test that /api/health/revision endpoint exists and has proper structure."""
    health_py = ROOT / "app" / "routers" / "health.py"
    content = health_py.read_text()
    
    # Verify revision endpoint exists
    assert '@router.get("/revision"' in content, \
        "Revision endpoint should be defined"
    
    assert 'summary="Deployment revision and version info (no auth)"' in content, \
        "Revision endpoint should have proper summary"
    
    # Verify it reads build_info.txt
    assert 'build_info.txt' in content, \
        "Revision endpoint should attempt to read build_info.txt"
    
    # Verify it uses pathlib for path construction
    assert 'from pathlib import Path' in content or 'Path(__file__)' in content, \
        "Revision endpoint should use pathlib for robust path handling"
    
    # Verify response structure
    assert '"build_info":' in content, \
        "Revision endpoint should include build_info in response"
    
    assert '"app_name":' in content, \
        "Revision endpoint should include app_name in response"
    
    print("✓ Health revision endpoint has correct structure")


def test_config_version_fields():
    """Test that config has version tracking fields defined."""
    config_py = ROOT / "app" / "core" / "config.py"
    content = config_py.read_text()
    
    # Check for version tracking fields
    assert 'git_commit_sha' in content, \
        "Config should have git_commit_sha field"
    
    assert 'build_timestamp' in content, \
        "Config should have build_timestamp field"
    
    assert 'app_version' in content, \
        "Config should have app_version field"
    
    # Check for get_version_info method
    assert 'def get_version_info' in content, \
        "Config should have get_version_info method"
    
    # Verify method returns dict with expected keys
    assert '"version":' in content or "'version':" in content, \
        "get_version_info should return dict with 'version' key"
    
    assert '"git_commit":' in content or "'git_commit':" in content, \
        "get_version_info should return dict with 'git_commit' key"
    
    assert '"environment":' in content or "'environment':" in content, \
        "get_version_info should return dict with 'environment' key"
    
    print("✓ Config has all required version tracking fields")


def test_exception_handling_in_revision_endpoint():
    """Test that revision endpoint has proper exception handling."""
    health_py = ROOT / "app" / "routers" / "health.py"
    content = health_py.read_text()
    
    # Verify specific exception types are caught
    assert ('IOError' in content and 'UnicodeDecodeError' in content), \
        "Revision endpoint should catch specific exceptions (IOError, UnicodeDecodeError)"
    
    # Verify it's not using bare except
    assert 'except Exception:' not in content or '(IOError, UnicodeDecodeError)' in content, \
        "Should use specific exception types, not bare 'except Exception:'"
    
    # Verify error handling provides feedback
    assert '"error"' in content or "'error'" in content, \
        "Exception handler should provide error feedback in response"
    
    print("✓ Revision endpoint has proper exception handling")


def test_no_unused_imports_in_config():
    """Test that there are no unused imports in config file."""
    config_py = ROOT / "app" / "core" / "config.py"
    content = config_py.read_text()
    
    lines = content.split('\n')
    
    # Check for datetime import at module level
    has_datetime_import = any('import datetime' in line or 'from datetime import' in line 
                              for line in lines[:20])  # Check first 20 lines
    
    if has_datetime_import:
        # If datetime is imported, verify it's used
        assert 'datetime.' in content or 'timedelta' in content, \
            "If datetime is imported, it should be used in the file"
    
    print("✓ No unused datetime import in config")


def test_pathlib_usage_in_health():
    """Test that health endpoints use pathlib for path construction."""
    health_py = ROOT / "app" / "routers" / "health.py"
    content = health_py.read_text()
    
    # Verify pathlib is imported
    assert 'from pathlib import Path' in content, \
        "Health module should import Path from pathlib"
    
    # Verify it's used for build_info.txt path
    assert 'Path(__file__)' in content, \
        "Should use Path(__file__) for robust path construction"
    
    assert '.parent.parent.parent' in content or '/ "build_info.txt"' in content, \
        "Should use pathlib methods to navigate directory structure"
    
    # Verify NOT using os.path.dirname
    assert 'os.path.dirname(os.path.dirname' not in content, \
        "Should not use fragile os.path.dirname chains"
    
    print("✓ Health endpoints use pathlib correctly")


def test_deployment_workflow_has_version_injection():
    """Test that deployment workflow injects version information."""
    workflow_file = ROOT.parent / ".github" / "workflows" / "deploy.yml"
    
    if not workflow_file.exists():
        print("⚠️  Deploy workflow file not found, skipping test")
        return
    
    content = workflow_file.read_text()
    
    # Verify environment variables are set
    assert 'GIT_COMMIT_SHA' in content, \
        "Deployment workflow should set GIT_COMMIT_SHA"
    
    assert 'BUILD_TIMESTAMP' in content, \
        "Deployment workflow should set BUILD_TIMESTAMP"
    
    assert 'APP_VERSION' in content, \
        "Deployment workflow should set APP_VERSION"
    
    # Verify build_info.txt generation
    assert 'build_info.txt' in content, \
        "Deployment workflow should generate build_info.txt"
    
    print("✓ Deployment workflow injects version information")


def test_diagnostic_script_has_jq_check():
    """Test that diagnostic script checks for jq availability."""
    script_file = ROOT.parent / "scripts" / "diagnose_azure_backend.sh"
    
    if not script_file.exists():
        print("⚠️  Diagnostic script not found, skipping test")
        return
    
    content = script_file.read_text()
    
    # Verify jq availability check
    assert 'command -v jq' in content, \
        "Diagnostic script should check if jq is available"
    
    assert 'JQ_AVAILABLE' in content, \
        "Diagnostic script should track jq availability"
    
    # Verify graceful degradation
    assert 'if [ "$JQ_AVAILABLE" = true ]' in content or 'if [ "$JQ_AVAILABLE" = "true" ]' in content, \
        "Diagnostic script should conditionally use jq"
    
    print("✓ Diagnostic script checks for jq availability")


def test_diagnostic_script_handles_interactive_prompts():
    """Test that diagnostic script properly handles interactive prompts with set -e."""
    script_file = ROOT.parent / "scripts" / "diagnose_azure_backend.sh"
    
    if not script_file.exists():
        print("⚠️  Diagnostic script not found, skipping test")
        return
    
    content = script_file.read_text()
    
    # Verify set -e is used
    assert 'set -e' in content, \
        "Diagnostic script should use set -e for error handling"
    
    # Verify interactive prompts are protected
    if 'read -p' in content:
        # Find the read prompt section
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'read -p' in line:
                # Check surrounding lines for set +e / set -e
                context = '\n'.join(lines[max(0, i-5):min(len(lines), i+5)])
                assert 'set +e' in context and 'set -e' in context, \
                    "Interactive prompts should be wrapped with set +e / set -e"
                break
    
    print("✓ Diagnostic script handles interactive prompts correctly")


if __name__ == "__main__":
    # Run all tests
    tests = [
        test_health_ping_endpoint_structure,
        test_health_revision_endpoint_structure,
        test_config_version_fields,
        test_exception_handling_in_revision_endpoint,
        test_no_unused_imports_in_config,
        test_pathlib_usage_in_health,
        test_deployment_workflow_has_version_injection,
        test_diagnostic_script_has_jq_check,
        test_diagnostic_script_handles_interactive_prompts,
    ]
    
    failed = []
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"⚠️  {test.__name__} error: {e}")
            failed.append(test.__name__)
    
    if failed:
        print(f"\n❌ {len(failed)} test(s) failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("\n✅ All health endpoint tests passed!")
        sys.exit(0)

