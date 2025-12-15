import os
import mysql.connector
from mysql.connector import Error
from hardcoded_database.consts import URL_RETENTION_MONTHS
from pylib.utils.network import resolve_host

class DBManager:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST')
        self.user = os.getenv('MYSQL_USER')
        self.password = os.getenv('MYSQL_PASSWORD')
        self.database = os.getenv('MYSQL_DATABASE')
        self.port = int(os.getenv('MYSQL_PORT', 3306))
        self._connection = None

    @property
    def connection(self):
        if self._connection is None or not self._connection.is_connected():
            # Resolve host manually with a short timeout to avoid long DNS delays
            host_ip = resolve_host(self.host)

            self._connection = mysql.connector.connect(
                host=host_ip,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                connection_timeout=1
            )
        return self._connection

    def close_connection(self):
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def init_db(self):
        """Initialize the database schema."""
        conn = self.connection
        if conn:
            try:
                cursor = conn.cursor()
                # Create url_mappings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS url_mappings (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        short_code VARCHAR(10) NOT NULL UNIQUE,
                        long_url MEDIUMTEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create trick_suggestions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trick_suggestions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        prop_type VARCHAR(50) NOT NULL,
                        name VARCHAR(255),
                        siteswap_x VARCHAR(255),
                        props_count INT,
                        difficulty INT,
                        max_throw INT,
                        tags TEXT,
                        comment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                cursor.close()
                print("Database initialized successfully.")
            except Error as e:
                print(f"Error initializing database: {e}")
        else:
            print("Failed to connect to database for initialization.")

    def get_short_code_by_long_url(self, long_url):
        conn = self.connection
        cursor = conn.cursor()
        # Note: querying by TEXT/MEDIUMTEXT can be slow on large datasets
        # but sufficient for this use case.
        cursor.execute(
            "SELECT short_code FROM url_mappings WHERE long_url = %s LIMIT 1",
            (long_url,)
        )
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result[0]
        return None

    def create_short_url(self, short_code, long_url):
        conn = self.connection
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO url_mappings (short_code, long_url) VALUES (%s, %s)",
            (short_code, long_url)
        )
        conn.commit()
        cursor.close()
        return True

    def get_long_url(self, short_code):
        conn = self.connection
        cursor = conn.cursor()
        cursor.execute(
            "SELECT long_url FROM url_mappings WHERE short_code = %s",
            (short_code,)
        )
        result = cursor.fetchone()
        cursor.close()
        if result:
            self.update_last_accessed(short_code)
            return result[0]
        return None

    def update_last_accessed(self, short_code):
        """Update the last_accessed_at timestamp for a given short code."""
        conn = self.connection
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE url_mappings SET last_accessed_at = CURRENT_TIMESTAMP WHERE short_code = %s",
                    (short_code,)
                )
                conn.commit()
                cursor.close()
            except Error as e:
                print(f"Error updating last accessed time: {e}")

    def delete_inactive_urls(self, months=URL_RETENTION_MONTHS):
        """Delete URLs that haven't been accessed for the specified number of months."""
        conn = self.connection
        deleted_count = 0
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM url_mappings WHERE last_accessed_at < DATE_SUB(NOW(), INTERVAL %s MONTH)",
                    (months,)
                )
                deleted_count = cursor.rowcount
                conn.commit()
                cursor.close()
                print(f"Deleted {deleted_count} inactive URLs.")
            except Error as e:
                print(f"Error deleting inactive URLs: {e}")
        return deleted_count

    def add_trick_suggestion(self, prop_type, name, siteswap_x, props_count, difficulty, max_throw, tags, comment):
        conn = self.connection
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO trick_suggestions
                    (prop_type, name, siteswap_x, props_count, difficulty, max_throw, tags, comment)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (prop_type, name, siteswap_x, props_count, difficulty, max_throw, tags, comment)
                )
                conn.commit()
                cursor.close()
                return True
            except Error as e:
                print(f"Error adding trick suggestion: {e}")
                return False
        return False

    def get_suggestions(self, prop_type):
        conn = self.connection
        suggestions = []
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    # Select columns in the exact order of balls.csv: name,props_count,difficulty,tags,comment,max_throw,siteswap_x
                    "SELECT name, props_count, difficulty, tags, comment, max_throw, siteswap_x FROM trick_suggestions WHERE prop_type = %s ORDER BY created_at DESC",
                    (prop_type,)
                )
                suggestions = cursor.fetchall()
                cursor.close()
            except Error as e:
                print(f"Error fetching suggestions: {e}")
        return suggestions

    def delete_suggestions(self, prop_type):
        conn = self.connection
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM trick_suggestions WHERE prop_type = %s",
                    (prop_type,)
                )
                conn.commit()
                cursor.close()
                return True
            except Error as e:
                print(f"Error deleting suggestions: {e}")
                return False
        return False

# Global instance
db_manager = DBManager()