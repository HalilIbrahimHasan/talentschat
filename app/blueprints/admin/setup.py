"""
One-time setup endpoint for initializing database
Can be called via HTTP since Shell is not available on free tier
"""
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.user import User
from app.models.learning import CodingChallenge
import json
import sys

bp = Blueprint('setup', __name__)


@bp.route('/setup/init', methods=['GET', 'POST'])
def init_database():
    """Initialize database - creates tables and admin user"""
    try:
        # Create all tables
        db.create_all()
        
        # Create admin user
        admin_email = "admin@talentschat.com"
        admin_name = "Admin User"
        admin_password = "admin123"
        
        existing_admin = User.query.filter_by(email=admin_email).first()
        if existing_admin:
            existing_admin.name = admin_name
            existing_admin.set_password(admin_password)
            existing_admin.is_admin = True
            db.session.commit()
            admin_status = "updated"
        else:
            admin_user = User(
                email=admin_email,
                name=admin_name,
                is_admin=True
            )
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            admin_status = "created"
        
        return jsonify({
            'success': True,
            'message': 'Database initialized successfully',
            'admin_user': admin_status,
            'admin_email': admin_email,
            'admin_password': admin_password
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/setup/add-challenges', methods=['GET', 'POST'])
def add_challenges():
    """Add Python coding challenges"""
    try:
        # Import the challenges from add_python_challenges.py logic
        # For simplicity, add a few basic challenges
        challenges_data = [
            {
                "title": "Hello World",
                "description": "Write a function that returns the string 'Hello, World!'",
                "difficulty": "easy",
                "starter_code": "def hello_world():\n    # Your code here\n    pass",
                "test_cases": [{"input": "", "expected_output": "Hello, World!"}],
                "points": 5
            },
            {
                "title": "Sum Two Numbers",
                "description": "Write a function that takes two numbers and returns their sum.",
                "difficulty": "easy",
                "starter_code": "def sum_numbers(a, b):\n    # Your code here\n    pass",
                "test_cases": [
                    {"input": "2, 3", "expected_output": "5"},
                    {"input": "-1, 1", "expected_output": "0"},
                    {"input": "0, 0", "expected_output": "0"}
                ],
                "points": 5
            }
        ]
        
        added = 0
        for challenge_data in challenges_data:
            existing = CodingChallenge.query.filter_by(title=challenge_data["title"]).first()
            if not existing:
                challenge = CodingChallenge(
                    title=challenge_data["title"],
                    description=challenge_data["description"],
                    difficulty=challenge_data["difficulty"],
                    starter_code=challenge_data["starter_code"],
                    test_cases_json=json.dumps(challenge_data["test_cases"]),
                    points=challenge_data["points"],
                    is_active=True
                )
                db.session.add(challenge)
                added += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Added {added} challenges',
            'total_challenges': CodingChallenge.query.count()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

