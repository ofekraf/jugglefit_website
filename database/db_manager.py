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

# Global instance
db_manager = DBManager()