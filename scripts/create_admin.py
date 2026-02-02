#!/usr/bin/env python3
"""
Create Admin User Script
Creates the first admin user and organization in the PostgreSQL database.
"""

import os
import sys
from getpass import getpass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.pg_auth_manager import PostgreSQLAuthManager
from auth.models import UserCreate


def create_admin():
    """Interactive script to create an admin user."""
    print("=" * 60)
    print("Create Admin User - Enterprise Knowledge Graph")
    print("=" * 60)
    print()
    
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print()
        print("Please set DATABASE_URL in your environment:")
        print("  export DATABASE_URL=postgresql://user:password@localhost/ekg_auth")
        print()
        print("Or create a .env file with:")
        print("  DATABASE_URL=postgresql://user:password@localhost/ekg_auth")
        sys.exit(1)
    
    print("This script will create:")
    print("  1. A new organization")
    print("  2. An admin user for that organization")
    print()
    
    # Get organization details
    print("Organization Details")
    print("-" * 60)
    org_name = input("Organization Name: ").strip()
    if not org_name:
        print("❌ Organization name cannot be empty")
        sys.exit(1)
    
    print()
    print("Available Plans:")
    print("  1. FREE")
    print("  2. STARTER")
    print("  3. PROFESSIONAL")
    print("  4. ENTERPRISE")
    plan_choice = input("Choose plan (1-4) [default: 4]: ").strip() or "4"
    
    plan_map = {
        "1": "FREE",
        "2": "STARTER",
        "3": "PROFESSIONAL",
        "4": "ENTERPRISE"
    }
    plan = plan_map.get(plan_choice, "ENTERPRISE")
    
    # Get user details
    print()
    print("Admin User Details")
    print("-" * 60)
    email = input("Email: ").strip()
    if not email or '@' not in email:
        print("❌ Invalid email address")
        sys.exit(1)
    
    full_name = input("Full Name: ").strip()
    
    password = getpass("Password (min 8 characters): ")
    password_confirm = getpass("Confirm Password: ")
    
    if password != password_confirm:
        print("❌ Passwords do not match")
        sys.exit(1)
    
    if len(password) < 8:
        print("❌ Password must be at least 8 characters")
        sys.exit(1)
    
    # Create organization and user
    print()
    print("Creating organization and user...")
    print("-" * 60)
    
    try:
        auth_manager = PostgreSQLAuthManager()
        
        # Check if organization already exists
        from auth.database import get_db
        from auth.db_models import Organization
        
        db = next(get_db())
        existing_org = db.query(Organization).filter(Organization.name == org_name).first()
        
        if existing_org:
            print(f"ℹ️  Organization '{org_name}' already exists")
            org_id = existing_org.id
        else:
            org = auth_manager.create_organization(org_name, plan)
            org_id = org.id
            print(f"✅ Organization created: {org_name} (Plan: {plan})")
        
        # Create admin user
        user_data = UserCreate(
            email=email,
            password=password,
            full_name=full_name,
            organization_name=org_name,
            role="admin"
        )
        
        user = auth_manager.register_user(user_data)
        
        print(f"✅ Admin user created: {email}")
        print()
        print("=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print()
        print("You can now login with:")
        print(f"  Email: {email}")
        print(f"  Organization: {org_name}")
        print()
        print("Start the backend:")
        print("  python main.py")
        print()
        print("Then access the frontend:")
        print("  http://localhost:3000")
        print()
        
    except Exception as e:
        print(f"❌ Failed to create user: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
