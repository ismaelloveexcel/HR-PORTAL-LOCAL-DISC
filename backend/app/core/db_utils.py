"""Database utilities for URL handling and SSL configuration."""

import re
from typing import Tuple


def clean_database_url_for_asyncpg(url: str) -> Tuple[str, bool]:
    """
    Clean a PostgreSQL connection URL for use with asyncpg.
    
    Asyncpg doesn't support SSL parameters in the URL itself; they must be
    passed via connect_args. This function:
    1. Detects if SSL is required (sslmode=require or ssl=require)
    2. Removes SSL parameters from the URL
    3. Converts postgresql:// or postgres:// to postgresql+asyncpg://
    
    Args:
        url: PostgreSQL connection URL (e.g., "postgresql://user:pass@host:5432/db?sslmode=require")
        
    Returns:
        Tuple of (cleaned_url, ssl_required)
        - cleaned_url: URL without SSL parameters, ready for asyncpg
        - ssl_required: True if SSL should be used (pass to connect_args)
    
    Examples:
        >>> clean_database_url_for_asyncpg("postgresql://host:5432/db?sslmode=require")
        ('postgresql+asyncpg://host:5432/db', True)
        
        >>> clean_database_url_for_asyncpg("postgresql://host:5432/db")
        ('postgresql+asyncpg://host:5432/db', False)
    """
    db_url = url
    
    # Convert standard postgres URL to asyncpg format
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    # Check if SSL is required in the connection string
    ssl_required = "sslmode=require" in db_url or "ssl=require" in db_url
    
    # Remove sslmode/ssl parameters from URL (asyncpg uses connect_args instead)
    # This regex handles multiple edge cases:
    # - ?sslmode=require -> (removed)
    # - ?sslmode=require&other=param -> ?other=param
    # - ?other=param&sslmode=require -> ?other=param
    # - ?p1=v1&sslmode=require&p2=v2 -> ?p1=v1&p2=v2
    def _replace_param(match):
        """Replace SSL parameter while maintaining valid query string format."""
        if match.group(0)[0] == '?' and match.group(1):
            # First param being removed and there's more params
            return '?'
        else:
            # Middle/last param being removed
            return match.group(1)
    
    db_url = re.sub(r'[?&]sslmode=[^&]*(&|$)', _replace_param, db_url)
    db_url = re.sub(r'[?&]ssl=[^&]*(&|$)', _replace_param, db_url)
    
    # Clean up any trailing ? or &
    db_url = db_url.rstrip('?&')
    
    return db_url, ssl_required
