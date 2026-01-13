#!/usr/bin/env python3
"""
Complete setup script for PostgreSQL database:
1. Creates all tables
2. Creates admin user
3. Adds Python coding challenges
4. Adds English lessons (optional)
"""
import os
import sys

# Set DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://talentschatdb_user:PexPT6558fFTGuly9RSPIe92nbVEMzEu@dpg-d5ir02n5r7bs73dk7cv0-a.oregon-postgres.render.com:5432/talentschatdb'

if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

os.environ['DATABASE_URL'] = DATABASE_URL

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.learning import CodingChallenge

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
            print(f"⚠️  Admin user already exists, updating password...")
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
        
        print(f"\n✅ Admin user verified: {admin.email}")
        
        return True

def add_python_challenges():
    """Add Python coding challenges"""
    
    with app.app_context():
        from app.models.learning import CodingChallenge
        from app.models.user import User
        
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("❌ Admin user not found. Run setup_database() first.")
            return False
        
        print("\n🐍 Adding Python coding challenges...")
        
        # Check if challenges already exist
        existing = CodingChallenge.query.count()
        if existing > 0:
            print(f"⚠️  {existing} coding challenges already exist. Skipping...")
            response = input("Do you want to add more anyway? (y/n): ").strip().lower()
            if response != 'y':
                return True
        
        challenges_data = [
            {
                'title': 'Hello World',
                'description': 'Write a Python program that prints "Hello, World!"',
                'starter_code': 'print("Hello, World!")',
                'test_code': '''
def test_solution():
    import io
    import sys
    from solution import *
    
    captured_output = io.StringIO()
    sys.stdout = captured_output
    # Solution code will be executed here
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue().strip()
    assert output == "Hello, World!", f"Expected 'Hello, World!' but got '{output}'"
    return True
''',
                'difficulty': 'easy',
                'points': 10
            },
            {
                'title': 'Sum Two Numbers',
                'description': 'Write a function that takes two numbers and returns their sum.',
                'starter_code': 'def add(a, b):\n    # Your code here\n    pass',
                'test_code': '''
def test_solution():
    from solution import add
    assert add(2, 3) == 5, "add(2, 3) should return 5"
    assert add(-1, 1) == 0, "add(-1, 1) should return 0"
    assert add(0, 0) == 0, "add(0, 0) should return 0"
    return True
''',
                'difficulty': 'easy',
                'points': 15
            },
            {
                'title': 'Factorial',
                'description': 'Write a function that calculates the factorial of a number.',
                'starter_code': 'def factorial(n):\n    # Your code here\n    pass',
                'test_code': '''
def test_solution():
    from solution import factorial
    assert factorial(0) == 1, "factorial(0) should return 1"
    assert factorial(1) == 1, "factorial(1) should return 1"
    assert factorial(5) == 120, "factorial(5) should return 120"
    return True
''',
                'difficulty': 'medium',
                'points': 20
            },
            {
                'title': 'Reverse String',
                'description': 'Write a function that reverses a string without using built-in reverse methods.',
                'starter_code': 'def reverse_string(s):\n    # Your code here\n    pass',
                'test_code': '''
def test_solution():
    from solution import reverse_string
    assert reverse_string("hello") == "olleh", "reverse_string('hello') should return 'olleh'"
    assert reverse_string("") == "", "reverse_string('') should return ''"
    assert reverse_string("a") == "a", "reverse_string('a') should return 'a'"
    return True
''',
                'difficulty': 'easy',
                'points': 15
            },
            {
                'title': 'Find Maximum',
                'description': 'Write a function that finds the maximum number in a list.',
                'starter_code': 'def find_max(numbers):\n    # Your code here\n    pass',
                'test_code': '''
def test_solution():
    from solution import find_max
    assert find_max([1, 2, 3, 4, 5]) == 5, "find_max([1,2,3,4,5]) should return 5"
    assert find_max([-1, -5, -3]) == -1, "find_max([-1,-5,-3]) should return -1"
    assert find_max([42]) == 42, "find_max([42]) should return 42"
    return True
''',
                'difficulty': 'easy',
                'points': 15
            }
        ]
        
        created = 0
        for challenge_data in challenges_data:
            # Check if challenge with same title exists
            existing = CodingChallenge.query.filter_by(title=challenge_data['title']).first()
            if existing:
                print(f"   ⏭️  Challenge '{challenge_data['title']}' already exists, skipping...")
                continue
            
            challenge = CodingChallenge(
                title=challenge_data['title'],
                description=challenge_data['description'],
                starter_code=challenge_data['starter_code'],
                test_code=challenge_data['test_code'],
                difficulty=challenge_data['difficulty'],
                points=challenge_data['points']
            )
            db.session.add(challenge)
            created += 1
            print(f"   ✅ Created challenge: {challenge_data['title']}")
        
        db.session.commit()
        print(f"\n✅ Created {created} Python coding challenges")
        
        return True

if __name__ == '__main__':
    print("\n🔧 Starting database setup...\n")
    
    # Step 1: Setup database and admin user
    if not setup_database():
        print("\n❌ Database setup failed!")
        sys.exit(1)
    
    # Step 2: Add Python challenges
    if not add_python_challenges():
        print("\n⚠️  Failed to add Python challenges, but database is set up")
    
    print("\n" + "=" * 70)
    print("✅ Setup Complete!")
    print("=" * 70)
    print("\n🔑 Admin Credentials:")
    print("   Email: admin@talentschat.com")
    print("   Password: admin123")
    print("\n🌐 Next Steps:")
    print("   1. Make sure DATABASE_URL is set in Render dashboard")
    print("   2. Deploy your app")
    print("   3. Login with admin credentials")
    print("=" * 70)

