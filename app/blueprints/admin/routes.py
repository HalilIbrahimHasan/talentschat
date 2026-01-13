"""Admin routes for learning content management"""
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.blueprints.admin import bp
from app.models.learning import (
    Portal, Lesson, Quiz, QuizQuestion, Task, CodingChallenge
)
from app.models.user import User
from app.extensions import db
from app.utils.youtube import extract_youtube_id
from app.services.scoring import update_quiz_total_points
import json


def require_admin():
    """Check if current user is admin - only admin users can access"""
    if not current_user.is_authenticated:
        abort(403)
    if not current_user.is_admin:
        from flask import flash, redirect, url_for
        flash('Access denied. Admin privileges required.', 'error')
        abort(403)


@bp.route('/setup/init', methods=['GET', 'POST'])
def init_database():
    """Initialize database - creates tables and admin user - NO AUTH REQUIRED"""
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
        
        # Verify
        admin = User.query.filter_by(email=admin_email).first()
        total_users = User.query.count()
        
        return jsonify({
            'success': True,
            'message': 'Database initialized successfully',
            'admin_user': admin_status,
            'admin_email': admin_email,
            'admin_password': admin_password,
            'total_users': total_users,
            'admin_exists': admin is not None,
            'admin_is_admin': admin.is_admin if admin else False
        }), 200
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@bp.route('/setup/status', methods=['GET'])
def check_status():
    """Check database connection and status - NO AUTH REQUIRED"""
    try:
        # Test connection
        db.engine.connect().close()
        connection_status = "connected"
    except Exception as e:
        connection_status = f"error: {str(e)}"
    
    try:
        # Check tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        users_table_exists = 'users' in tables
    except Exception as e:
        tables = []
        users_table_exists = False
    
    try:
        # Check admin user
        admin = User.query.filter_by(email="admin@talentschat.com").first()
        admin_exists = admin is not None
        admin_is_admin = admin.is_admin if admin else False
        total_users = User.query.count()
    except Exception as e:
        admin_exists = False
        admin_is_admin = False
        total_users = 0
    
    try:
        # Check database URL
        from app import create_app
        import os
        database_url = os.environ.get('DATABASE_URL', 'NOT SET')
        if database_url and len(database_url) > 50:
            database_url_display = database_url[:30] + "..." + database_url[-20:]
        else:
            database_url_display = database_url
    except:
        database_url_display = "unknown"
    
    return jsonify({
        'connection': connection_status,
        'database_url_set': database_url_display != 'NOT SET',
        'database_url_preview': database_url_display,
        'tables_exist': len(tables) > 0,
        'users_table_exists': users_table_exists,
        'total_tables': len(tables),
        'admin_exists': admin_exists,
        'admin_is_admin': admin_is_admin,
        'total_users': total_users
    }), 200


@bp.route('/setup/add-challenges', methods=['GET', 'POST'])
def add_challenges():
    """Add Python coding challenges - NO AUTH REQUIRED"""
    try:
        # Add a few basic challenges
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
        
        total = CodingChallenge.query.count()
        
        return jsonify({
            'success': True,
            'message': f'Added {added} challenges',
            'added': added,
            'total_challenges': total
        }), 200
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@bp.route('/learn')
@login_required
def learn_dashboard():
    """Admin dashboard for learning content"""
    require_admin()
    try:
        portals = Portal.query.order_by(Portal.id).all()
        coding_challenges = CodingChallenge.query.filter_by(is_active=True).order_by(CodingChallenge.id).all()
        return render_template('admin/learn_dashboard.html', portals=portals, coding_challenges=coding_challenges)
    except Exception as e:
        import traceback
        # Log error and return friendly message
        print(f"Error in learn_dashboard: {e}")
        print(traceback.format_exc())
        flash(f'Error loading admin dashboard: {str(e)}', 'error')
        # Return empty lists if query fails
        return render_template('admin/learn_dashboard.html', portals=[], coding_challenges=[])


# Portal management routes (stubs - to be implemented)
@bp.route('/portal/create', methods=['GET', 'POST'])
@login_required
def create_portal():
    """Create a new portal - placeholder"""
    require_admin()
    flash('Portal creation feature is not yet implemented.', 'info')
    return redirect(url_for('admin.learn_dashboard'))


@bp.route('/portal/<int:portal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_portal(portal_id):
    """Edit a portal - placeholder"""
    require_admin()
    flash('Portal editing feature is not yet implemented.', 'info')
    return redirect(url_for('admin.learn_dashboard'))


@bp.route('/portal/<int:portal_id>/delete', methods=['POST'])
@login_required
def delete_portal(portal_id):
    """Delete a portal - placeholder"""
    require_admin()
    flash('Portal deletion feature is not yet implemented.', 'info')
    return redirect(url_for('admin.learn_dashboard'))


@bp.route('/portal/<int:portal_id>/lessons')
@login_required
def portal_lessons(portal_id):
    """View lessons for a portal - placeholder"""
    require_admin()
    flash('Portal lessons view is not yet implemented.', 'info')
    return redirect(url_for('admin.learn_dashboard'))


# Coding challenge management routes (stubs - to be implemented)
@bp.route('/coding-challenge/create', methods=['GET', 'POST'])
@login_required
def create_coding_challenge():
    """Create a new coding challenge - placeholder"""
    require_admin()
    flash('Coding challenge creation feature is not yet implemented.', 'info')
    return redirect(url_for('admin.learn_dashboard'))


@bp.route('/coding-challenge/<int:challenge_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_coding_challenge(challenge_id):
    """Edit a coding challenge - placeholder"""
    require_admin()
    flash('Coding challenge editing feature is not yet implemented.', 'info')
    return redirect(url_for('admin.learn_dashboard'))


@bp.route('/coding-challenge/<int:challenge_id>/delete', methods=['POST'])
@login_required
def delete_coding_challenge(challenge_id):
    """Delete a coding challenge - placeholder"""
    require_admin()
    flash('Coding challenge deletion feature is not yet implemented.', 'info')
    return redirect(url_for('admin.learn_dashboard'))
