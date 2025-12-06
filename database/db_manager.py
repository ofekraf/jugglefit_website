import os
import mysql.connector
from mysql.connector import Error
import time

class DBManager:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST')
        self.user = os.getenv('MYSQL_USER')
        self.password = os.getenv('MYSQL_PASSWORD')
        self.database = os.getenv('MYSQL_DATABASE')
        self.port = int(os.getenv('MYSQL_PORT', 3306))
        self.connection = None

    def get_connection(self):
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port
                )
            except Error as e:
                print(f"Error connecting to MySQL: {e}")
                return None
        return self.connection

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def init_db(self):
        """Initialize the database schema."""
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Create url_mappings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS url_mappings (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        short_code VARCHAR(10) NOT NULL UNIQUE,
                        long_url MEDIUMTEXT NOT NULL,
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
        conn = self.get_connection()
        if conn:
            try:
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
            except Error as e:
                print(f"Error retrieving short code: {e}")
        return None

    def create_short_url(self, short_code, long_url):
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO url_mappings (short_code, long_url) VALUES (%s, %s)",
                    (short_code, long_url)
                )
                conn.commit()
                cursor.close()
                return True
            except Error as e:
                print(f"Error creating short URL: {e}")
                return False
        return False

    def get_long_url(self, short_code):
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT long_url FROM url_mappings WHERE short_code = %s",
                    (short_code,)
                )
                result = cursor.fetchone()
                cursor.close()
                if result:
                    return result[0]
            except Error as e:
                print(f"Error retrieving long URL: {e}")
        return None

# Global instance
db_manager = DBManager()