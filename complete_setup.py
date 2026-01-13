#!/usr/bin/env python3
"""
Complete setup script for PostgreSQL database:
1. Creates all tables
2. Creates admin user
3. Adds Python coding challenges (100 challenges)
"""
import os
import sys

# Set DATABASE_URL - This should match your Render PostgreSQL database
DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://talentschatdb_user:PexPT6558fFTGuly9RSPIe92nbVEMzEu@dpg-d5ir02n5r7bs73dk7cv0-a.oregon-postgres.render.com:5432/talentschatdb'

if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

os.environ['DATABASE_URL'] = DATABASE_URL

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.learning import CodingChallenge
import json

app = create_app()

def setup_database():
    """Initialize database and create admin user"""
    
    with app.app_context():
        print("=" * 70)
        print("PostgreSQL Database Setup")
        print("=" * 70)
        
        # Create all tables
        print("\n📋 Creating all database tables...")
        try:
            db.create_all()
            print("✅ All tables created successfully")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Create admin user
        print("\n👤 Creating admin user...")
        admin_email = "admin@talentschat.com"
        admin_name = "Admin User"
        admin_password = "admin123"
        
        existing_admin = User.query.filter_by(email=admin_email).first()
        if existing_admin:
            print(f"⚠️  Admin user already exists, updating...")
            existing_admin.name = admin_name
            existing_admin.set_password(admin_password)
            existing_admin.is_admin = True
            db.session.commit()
            print(f"✅ Updated admin user: {admin_email}")
        else:
            admin_user = User(
                email=admin_email,
                name=admin_name,
                is_admin=True
            )
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            print(f"✅ Created admin user: {admin_email}")
        
        # Verify admin
        admin = User.query.filter_by(email=admin_email).first()
        if not admin or not admin.is_admin:
            print("❌ Failed to create admin user")
            return False
        
        print(f"✅ Admin user verified: {admin.email}")
        return True

def add_python_challenges():
    """Import and add Python coding challenges from add_python_challenges.py"""
    
    with app.app_context():
        print("\n🐍 Adding Python coding challenges...")
        
        # Import the challenges generator from the existing script
        try:
            # We'll use the existing add_python_challenges.py logic
            # But import it as a module would be complex, so let's just run it
            import subprocess
            result = subprocess.run(
                [sys.executable, 'add_python_challenges.py'],
                capture_output=True,
                text=True,
                env=os.environ
            )
            print(result.stdout)
            if result.returncode != 0:
                print(f"⚠️  Error: {result.stderr}")
                return False
            return True
        except Exception as e:
            print(f"⚠️  Could not run add_python_challenges.py: {e}")
            print("   You can run it separately: python3 add_python_challenges.py")
            return False

if __name__ == '__main__':
    print("\n🔧 Starting complete database setup...\n")
    
    # Step 1: Setup database and admin user
    if not setup_database():
        print("\n❌ Database setup failed!")
        sys.exit(1)
    
    # Step 2: Add Python challenges
    print("\n" + "=" * 70)
    print("Adding Python Coding Challenges")
    print("=" * 70)
    add_python_challenges()
    
    print("\n" + "=" * 70)
    print("✅ Setup Complete!")
    print("=" * 70)
    print("\n🔑 Admin Credentials:")
    print("   Email: admin@talentschat.com")
    print("   Password: admin123")
    print("\n📊 Next Steps:")
    print("   1. Make sure DATABASE_URL is set in Render dashboard")
    print("   2. Deploy your app")
    print("   3. Login with admin credentials")
    print("   4. Check /learn/coding-challenges to see Python challenges")
    print("=" * 70)

