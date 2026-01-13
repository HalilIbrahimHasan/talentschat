"""
Script to create the admin user.
Run this once: python3 create_admin.py
"""
from app import create_app
from app.models.user import User
from app.extensions import db

app = create_app()

with app.app_context():
    # Check if admin already exists
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        print(f"Admin user already exists: {admin.email}")
        print(f"To reset admin password, update user ID {admin.id} directly in the database.")
    else:
        # Create admin user
        email = input("Enter admin email: ").strip()
        name = input("Enter admin name: ").strip()
        password = input("Enter admin password: ").strip()
        
        if not email or not name or not password:
            print("Error: Email, name, and password are required")
            exit(1)
        
        # Check if user with this email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # Update existing user to be admin
            existing_user.is_admin = True
            existing_user.set_password(password)
            existing_user.name = name
            db.session.commit()
            print(f"✓ Updated existing user {email} to admin")
        else:
            # Create new admin user
            admin_user = User(
                email=email,
                name=name,
                is_admin=True
            )
            admin_user.set_password(password)
            db.session.add(admin_user)
            db.session.commit()
            print(f"✓ Created admin user: {email}")
        
        print("\nAdmin user created/updated successfully!")
        print("You can now log in with these credentials to access the admin panel.")



