"""
Database initialization script for PostgreSQL authentication.
Run this to set up the database tables.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from auth.database import engine, Base
from auth.db_models import User, Organization, RefreshToken, PasswordResetToken, EmailVerificationToken, AuditLog

def init_database():
    """Create all database tables."""
    print("🔧 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print("\nTables created:")
        print("  - users")
        print("  - organizations")
        print("  - refresh_tokens")
        print("  - password_reset_tokens")
        print("  - email_verification_tokens")
        print("  - audit_logs")
        print("\n📝 Next steps:")
        print("  1. Set DATABASE_URL environment variable")
        print("  2. Restart the application")
        print("  3. Register a new user at http://localhost:3000/register")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print("\n💡 Make sure:")
        print("  - PostgreSQL is running")
        print("  - DATABASE_URL is set correctly in .env")
        print("  - Database exists and is accessible")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
