"""
Database initialization script.
Run this to create all PostgreSQL tables.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from auth.database import init_db, engine
from auth.db_models import Base
from sqlalchemy import text


def create_database_if_not_exists():
    """Create database if it doesn't exist."""
    try:
        # Try to connect
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n📝 To create the database, run:")
        print("   createdb ekg_db")
        print("   # OR in psql:")
        print("   CREATE DATABASE ekg_db;")
        sys.exit(1)


def main():
    """Initialize database tables."""
    print("🗄️  EKG Database Initialization")
    print("=" * 50)
    
    # Check database connection
    create_database_if_not_exists()
    
    # Create tables
    print("\n📊 Creating database tables...")
    try:
        init_db()
        print("\n✅ Database initialized successfully!")
        print("\nCreated tables:")
        print("  - users")
        print("  - organizations")
        print("  - refresh_tokens")
        print("  - password_reset_tokens")
        print("  - email_verification_tokens")
        print("  - audit_logs")
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
