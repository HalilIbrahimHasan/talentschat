#!/usr/bin/env python3
"""
Quick test script to verify database connection and check if admin user exists
"""
import os
import sys

# Set DATABASE_URL if not set
DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://talentschatdb_user:PexPT6558fFTGuly9RSPIe92nbVEMzEu@dpg-d5ir02n5r7bs73dk7cv0-a.oregon-postgres.render.com:5432/talentschatdb'

if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

os.environ['DATABASE_URL'] = DATABASE_URL

from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    
    try:
        # Test connection
        print("\n1. Testing database connection...")
        db.engine.connect()
        print("   ✅ Database connection successful!")
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        sys.exit(1)
    
    try:
        # Check if tables exist
        print("\n2. Checking if tables exist...")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"   Found {len(tables)} tables: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}")
        
        if 'users' in tables:
            print("   ✅ Users table exists")
            
            # Check for admin user
            print("\n3. Checking for admin user...")
            admin = User.query.filter_by(is_admin=True).first()
            if admin:
                print(f"   ✅ Admin user found:")
                print(f"      Email: {admin.email}")
                print(f"      Name: {admin.name}")
                print(f"      Is Admin: {admin.is_admin}")
            else:
                print("   ⚠️  No admin user found")
                print("   Run init_postgres_db.py to create admin user")
        else:
            print("   ⚠️  Users table does not exist")
            print("   Run init_postgres_db.py to create tables")
    except Exception as e:
        print(f"   ❌ Error checking tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

