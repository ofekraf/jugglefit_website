import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional

# In-memory storage for URL mappings
url_storage: Dict[str, dict] = {}

def init_db():
    """Initialize the in-memory database (no-op for memory storage)"""
    pass

def start_cleanup_thread():
    """Start cleanup thread (no-op for memory storage)"""
    pass

def get_or_create_short_url(long_url: str) -> str:
    """Get existing short URL or create a new one for the given long URL"""
    # Check if long_url already exists
    for code, data in url_storage.items():
        if data['long_url'] == long_url:
            # Refresh expiry time
            data['expires_at'] = datetime.now() + timedelta(days=30)
            return code
    
    # Generate a unique 8-char code
    while True:
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        if code not in url_storage:
            break
    
    # Store with 30-day expiry
    url_storage[code] = {
        'long_url': long_url,
        'created_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(days=30)
    }
    
    return code

def get_long_url_and_refresh(code: str) -> Optional[str]:
    """Get long URL by short code and refresh expiry if needed"""
    if code not in url_storage:
        return None
    
    data = url_storage[code]
    
    # Check if expired
    if datetime.now() > data['expires_at']:
        del url_storage[code]
        return None
    
    # Refresh expiry if within 7 days of expiration
    if (data['expires_at'] - datetime.now()).days < 7:
        data['expires_at'] = datetime.now() + timedelta(days=30)
    
    return data['long_url']