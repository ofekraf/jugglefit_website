from app import app
from database.db_manager import db_manager
from hardcoded_database.consts import URL_RETENTION_MONTHS

# Initialize database when running in production (Gunicorn)
try:
    print("Attempting to initialize database...")
    db_manager.init_db()
    # Clean up inactive URLs on startup
    db_manager.delete_inactive_urls(URL_RETENTION_MONTHS)
except Exception as e:
    print(f"Failed to initialize database: {e}")

if __name__ == "__main__":
    app.run()