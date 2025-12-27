import os
import sqlite3
from sqlite3 import Error
from hardcoded_database.consts import URL_RETENTION_MONTHS

class DBManager:
    def __init__(self):
        # Use a directory that is mounted in docker-compose
        # Default to a local directory relative to CWD if env var not set (better for local dev)
        default_dir = os.path.join(os.getcwd(), 'database_data')
        self.db_dir = os.getenv('SQLITE_DB_DIR', default_dir)
        self.db_name = os.getenv('SQLITE_DB_NAME', 'jugglefit.db')
        self.db_path = os.path.join(self.db_dir, self.db_name)
        
        # Ensure directory exists if running locally without docker volume mapping pre-creation
        if not os.path.exists(self.db_dir):
            try:
                os.makedirs(self.db_dir)
            except OSError:
                # Might fail if permissions issue or if it's a file, but we'll try
                pass

    def get_connection(self):
        """Create a database connection to the SQLite database specified by db_path"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            # Enable dictionary access for rows
            conn.row_factory = sqlite3.Row
            return conn
        except Error as e:
            print(f"Error connecting to database: {e}")
        return conn

    @property
    def connection(self):
        # For backward compatibility with existing code that might access .connection
        # However, SQLite connections shouldn't be held open globally like the MySQL one was.
        # It's better to get a fresh connection per request/operation.
        return self.get_connection()

    def init_db(self):
        """Initialize the database schema."""
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Create url_mappings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS url_mappings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        short_code TEXT NOT NULL UNIQUE,
                        long_url TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create trick_suggestions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trick_suggestions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prop_type TEXT NOT NULL,
                        name TEXT,
                        siteswap_x TEXT,
                        props_count INTEGER,
                        difficulty INTEGER,
                        max_throw INTEGER,
                        tags TEXT,
                        comment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                print("Database initialized successfully.")
            except Error as e:
                print(f"Error initializing database: {e}")
            finally:
                conn.close()
        else:
            print("Failed to connect to database for initialization.")

    def get_short_code_by_long_url(self, long_url):
        conn = self.get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT short_code FROM url_mappings WHERE long_url = ? LIMIT 1",
                (long_url,)
            )
            result = cursor.fetchone()
            if result:
                return result['short_code']
            return None
        finally:
            conn.close()

    def create_short_url(self, short_code, long_url):
        conn = self.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO url_mappings (short_code, long_url) VALUES (?, ?)",
                (short_code, long_url)
            )
            conn.commit()
            return True
        except Error as e:
            print(f"Error creating short URL: {e}")
            return False
        finally:
            conn.close()

    def get_long_url(self, short_code):
        conn = self.get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT long_url FROM url_mappings WHERE short_code = ?",
                (short_code,)
            )
            result = cursor.fetchone()
            if result:
                self.update_last_accessed(short_code)
                return result['long_url']
            return None
        finally:
            conn.close()

    def update_last_accessed(self, short_code):
        """Update the last_accessed_at timestamp for a given short code."""
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE url_mappings SET last_accessed_at = CURRENT_TIMESTAMP WHERE short_code = ?",
                    (short_code,)
                )
                conn.commit()
            except Error as e:
                print(f"Error updating last accessed time: {e}")
            finally:
                conn.close()

    def delete_inactive_urls(self, months=URL_RETENTION_MONTHS):
        """Delete URLs that haven't been accessed for the specified number of months."""
        conn = self.get_connection()
        deleted_count = 0
        if conn:
            try:
                cursor = conn.cursor()
                # SQLite date math
                cursor.execute(
                    f"DELETE FROM url_mappings WHERE last_accessed_at < datetime('now', '-{months} months')"
                )
                deleted_count = cursor.rowcount
                conn.commit()
                print(f"Deleted {deleted_count} inactive URLs.")
            except Error as e:
                print(f"Error deleting inactive URLs: {e}")
            finally:
                conn.close()
        return deleted_count

    def add_trick_suggestion(self, prop_type, name, siteswap_x, props_count, difficulty, max_throw, tags, comment):
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO trick_suggestions
                    (prop_type, name, siteswap_x, props_count, difficulty, max_throw, tags, comment)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (prop_type, name, siteswap_x, props_count, difficulty, max_throw, tags, comment)
                )
                conn.commit()
                return True
            except Error as e:
                print(f"Error adding trick suggestion: {e}")
                return False
            finally:
                conn.close()
        return False

    def get_suggestions(self, prop_type):
        conn = self.get_connection()
        suggestions = []
        if conn:
            try:
                # sqlite3.Row factory allows dictionary-like access, but fetchall returns Row objects.
                # We can convert them to dicts if needed, but usually Row objects work fine in templates/json serialization if handled correctly.
                # However, for jsonify compatibility, it's safer to convert to dict.
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name, props_count, difficulty, tags, comment, max_throw, siteswap_x FROM trick_suggestions WHERE prop_type = ? ORDER BY created_at DESC",
                    (prop_type,)
                )
                rows = cursor.fetchall()
                suggestions = [dict(row) for row in rows]
            except Error as e:
                print(f"Error fetching suggestions: {e}")
            finally:
                conn.close()
        return suggestions

    def delete_suggestions(self, prop_type):
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM trick_suggestions WHERE prop_type = ?",
                    (prop_type,)
                )
                conn.commit()
                return True
            except Error as e:
                print(f"Error deleting suggestions: {e}")
                return False
            finally:
                conn.close()
        return False

# Global instance
db_manager = DBManager()