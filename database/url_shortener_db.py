import psycopg2
import random
import string
import threading
import time
import os
from datetime import datetime, timedelta
from database.hardcoded_config import (
    EXPIRED_URL_CLEANUP_INTERVAL, POSTGRESQL_DBNAME, POSTGRESQL_USERNAME, POSTGRESQL_PASSWORD, 
    POSTGRESQL_HOST, POSTGRESQL_PORT, SHORT_URL_EXPIRY_MONTHS, SHORT_URL_EXTEND_MONTHS
)

# Get configuration from environment variables with hardcoded fallbacks
DB_CONFIG = {
    'dbname': os.getenv('POSTGRESQL_DBNAME', POSTGRESQL_DBNAME),
    'user': os.getenv('POSTGRESQL_USERNAME', POSTGRESQL_USERNAME),
    'password': os.getenv('POSTGRESQL_PASSWORD', POSTGRESQL_PASSWORD),
    'host': os.getenv('POSTGRESQL_HOST', POSTGRESQL_HOST),
    'port': os.getenv('POSTGRESQL_PORT', POSTGRESQL_PORT)
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS short_urls (
                code VARCHAR(6) PRIMARY KEY,
                long_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '{URL_CONFIG["expiry_months"]} months')
            );
        """)
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

def get_or_create_short_url(long_url):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Check if long_url already exists
        cur.execute("SELECT code, expires_at FROM short_urls WHERE long_url = %s", (long_url,))
        row = cur.fetchone()
        if row:
            code = row[0]
            # Update expiry to N months from now
            cur.execute(f"UPDATE short_urls SET expires_at = (CURRENT_TIMESTAMP + INTERVAL '{URL_CONFIG['expiry_months']} months') WHERE code = %s", (code,))
            conn.commit()
            cur.close()
            return code
        # Generate a unique 8-char code
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            cur.execute("SELECT code FROM short_urls WHERE code = %s", (code,))
            if cur.fetchone() is None:
                break
        # Insert with expiry N months from now
        cur.execute(f"INSERT INTO short_urls (code, long_url, expires_at) VALUES (%s, %s, (CURRENT_TIMESTAMP + INTERVAL '{URL_CONFIG['expiry_months']} months'))", (code, long_url))
        conn.commit()
        cur.close()
        return code
    except Exception as e:
        pass
    finally:
        if conn:
            conn.close()

def get_long_url_and_refresh(code):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT long_url, expires_at FROM short_urls WHERE code = %s", (code,))
        result = cur.fetchone()
        if result:
            long_url, expires_at = result
            cur.execute("SELECT CURRENT_TIMESTAMP AT TIME ZONE 'UTC'")
            now = cur.fetchone()[0]
            # If expires_at is less than refresh days away, update to extend months ahead
            if expires_at and (expires_at - now).days < SHORT_URL_EXTEND_MONTHS:
                cur.execute(f"UPDATE short_urls SET expires_at = (CURRENT_TIMESTAMP + INTERVAL '{SHORT_URL_EXTEND_MONTHS} month') WHERE code = %s", (code,))
                conn.commit()
            cur.close()
            return long_url
        else:
            cur.close()
            return None
    finally:
        if conn:
            conn.close()

def delete_expired_urls():
    """
    Deletes all URLs that have expired.
    This function should be run periodically (e.g., via a cron job or scheduled task).
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Delete all URLs where expires_at is in the past
        cur.execute("DELETE FROM short_urls WHERE expires_at < CURRENT_TIMESTAMP")
        deleted_count = cur.rowcount
        conn.commit()
        cur.close()
        return deleted_count
    except Exception as e:
        print(f"Error deleting expired URLs: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def cleanup_thread():
    """
    Background thread that runs cleanup periodically
    """
    while True:
        try:
            print(f"[{datetime.now()}] Running expired URLs cleanup...")
            deleted_count = delete_expired_urls()
            print(f"[{datetime.now()}] Cleanup completed. Deleted {deleted_count} expired URLs")
        except Exception as e:
            print(f"[{datetime.now()}] Error in cleanup thread: {e}")
        
        # Sleep until next cleanup
        time.sleep(EXPIRED_URL_CLEANUP_INTERVAL)

def start_cleanup_thread():
    """
    Starts the background cleanup thread
    """
    thread = threading.Thread(target=cleanup_thread, daemon=True)
    thread.start()
    print(f"[{datetime.now()}] Started cleanup thread")
    return thread

