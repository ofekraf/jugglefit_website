import logging

from app import app
from database.db_manager import db_manager
from hardcoded_database.consts import URL_RETENTION_MONTHS

log = logging.getLogger(__name__)

# Initialize database when running in production (Gunicorn)
try:
    log.info("Initializing database...")
    db_manager.init_db()
    # Clean up inactive URLs on startup
    db_manager.delete_inactive_urls(URL_RETENTION_MONTHS)
    log.info("Database initialized.")
except Exception as e:
    log.exception("Failed to initialize database: %s", e)

if __name__ == "__main__":
    app.run()
