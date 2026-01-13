#!/usr/bin/env python3
"""
Script to initialize PostgreSQL database on Render.com
This script:
1. Connects to the PostgreSQL database
2. Creates all tables
3. Creates admin user with default credentials
4. Cleans up any existing data (fresh start)
"""
import os
import sys

# Set the DATABASE_URL environment variable for this script
# PostgreSQL connection string for Render.com database
# Format: postgresql://username:password@hostname:port/database
DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://talentschatdb_user:PexPT6558fFTGuly9RSPIe92nbVEMzEu@dpg-d5ir02n5r7bs73dk7cv0-a.oregon-postgres.render.com:5432/talentschatdb'

# Ensure postgresql:// (not postgres://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

os.environ['DATABASE_URL'] = DATABASE_URL

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.workspace import Workspace
from app.models.channel import Channel
from app.models.message import Message
from app.models.article import Article
from app.models.file import File
from app.models.video import Video
from app.models.learning import Portal, Lesson, Quiz, QuizQuestion, Task, CodingChallenge

app = create_app()

def init_database():
    """Initialize PostgreSQL database with schema and admin user"""
    
    with app.app_context():
        print("=" * 60)
        print("Initializing PostgreSQL Database on Render.com")
        print("=" * 60)
        
        # Drop all tables (fresh start)
        print("\n📋 Dropping all existing tables...")
        try:
            db.drop_all()
            print("✅ All tables dropped successfully")
        except Exception as e:
            print(f"⚠️  Error dropping tables (they may not exist): {e}")
        
        # Create all tables
        print("\n📋 Creating all tables...")
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
        
        # Check if admin already exists (shouldn't, but just in case)
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
        
        # Verify admin user
        admin = User.query.filter_by(email=admin_email).first()
        if admin and admin.is_admin:
            print(f"\n✅ Admin user verified:")
            print(f"   Email: {admin.email}")
            print(f"   Name: {admin.name}")
            print(f"   Is Admin: {admin.is_admin}")
        else:
            print("\n❌ Failed to verify admin user")
            return False
        
        # Show summary
        print("\n" + "=" * 60)
        print("✅ Database initialization complete!")
        print("=" * 60)
        print(f"\n📊 Database Summary:")
        print(f"   Total Users: {User.query.count()}")
        print(f"   Admin Users: {User.query.filter_by(is_admin=True).count()}")
        print(f"\n🔑 Admin Login Credentials:")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"\n🌐 Next Steps:")
        print(f"   1. Set DATABASE_URL environment variable in Render.com")
        print(f"   2. Deploy your application")
        print(f"   3. Login with admin credentials to access admin panel")
        print("=" * 60)
        
        return True

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)

