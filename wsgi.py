from app import app
from database.db_manager import db_manager

# Initialize database when running in production (Gunicorn)
try:
    print("Attempting to initialize database...")
    db_manager.init_db()
except Exception as e:
    print(f"Failed to initialize database: {e}")

if __name__ == "__main__":
    app.run()