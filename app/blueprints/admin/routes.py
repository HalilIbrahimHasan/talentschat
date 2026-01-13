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


# Portal management routes
@bp.route('/portal/create', methods=['GET', 'POST'])
@login_required
def create_portal():
    """Create a new portal"""
    require_admin()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Portal name is required.', 'error')
            return render_template('admin/portal_form.html', portal=None)
        
        portal = Portal(name=name, description=description if description else None)
        db.session.add(portal)
        db.session.commit()
        
        flash(f'Portal "{name}" created successfully!', 'success')
        return redirect(url_for('admin.portal_lessons', portal_id=portal.id))
    
    return render_template('admin/portal_form.html', portal=None)


@bp.route('/portal/<int:portal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_portal(portal_id):
    """Edit a portal"""
    require_admin()
    portal = Portal.query.get_or_404(portal_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Portal name is required.', 'error')
            return render_template('admin/portal_form.html', portal=portal)
        
        portal.name = name
        portal.description = description if description else None
        db.session.commit()
        
        flash(f'Portal "{name}" updated successfully!', 'success')
        return redirect(url_for('admin.learn_dashboard'))
    
    return render_template('admin/portal_form.html', portal=portal)


@bp.route('/portal/<int:portal_id>/delete', methods=['POST'])
@login_required
def delete_portal(portal_id):
    """Delete a portal"""
    require_admin()
    portal = Portal.query.get_or_404(portal_id)
    portal_name = portal.name
    
    db.session.delete(portal)
    db.session.commit()
    
    flash(f'Portal "{portal_name}" deleted successfully!', 'success')
    return redirect(url_for('admin.learn_dashboard'))


@bp.route('/portal/<int:portal_id>/lessons')
@login_required
def portal_lessons(portal_id):
    """View lessons for a portal"""
    require_admin()
    portal = Portal.query.get_or_404(portal_id)
    lessons = Lesson.query.filter_by(portal_id=portal_id).order_by(Lesson.order_index, Lesson.id).all()
    
    return render_template('admin/portal_lessons.html', portal=portal, lessons=lessons)


# Lesson management routes
@bp.route('/lesson/create/<int:portal_id>', methods=['GET', 'POST'])
@login_required
def create_lesson(portal_id):
    """Create a new lesson"""
    require_admin()
    portal = Portal.query.get_or_404(portal_id)
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        youtube_url = request.form.get('youtube_url', '').strip()
        points_complete = int(request.form.get('points_complete', 10) or 10)
        order_index = int(request.form.get('order_index', 0) or 0)
        
        if not title:
            flash('Lesson title is required.', 'error')
            return render_template('admin/lesson_form.html', portal=portal, lesson=None)
        
        youtube_id = extract_youtube_id(youtube_url) if youtube_url else None
        
        lesson = Lesson(
            portal_id=portal_id,
            title=title,
            description=description if description else None,
            youtube_url=youtube_url if youtube_url else None,
            youtube_id=youtube_id,
            points_complete=points_complete,
            order_index=order_index,
            is_active=True
        )
        db.session.add(lesson)
        db.session.commit()
        
        flash(f'Lesson "{title}" created successfully!', 'success')
        return redirect(url_for('admin.portal_lessons', portal_id=portal_id))
    
    return render_template('admin/lesson_form.html', portal=portal, lesson=None)


@bp.route('/lesson/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    """Edit a lesson"""
    require_admin()
    lesson = Lesson.query.get_or_404(lesson_id)
    portal = lesson.portal
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        youtube_url = request.form.get('youtube_url', '').strip()
        points_complete = int(request.form.get('points_complete', 10) or 10)
        order_index = int(request.form.get('order_index', 0) or 0)
        
        if not title:
            flash('Lesson title is required.', 'error')
            return render_template('admin/lesson_form.html', portal=portal, lesson=lesson)
        
        lesson.title = title
        lesson.description = description if description else None
        lesson.youtube_url = youtube_url if youtube_url else None
        lesson.youtube_id = extract_youtube_id(youtube_url) if youtube_url else None
        lesson.points_complete = points_complete
        lesson.order_index = order_index
        db.session.commit()
        
        flash(f'Lesson "{title}" updated successfully!', 'success')
        return redirect(url_for('admin.portal_lessons', portal_id=portal.id))
    
    return render_template('admin/lesson_form.html', portal=portal, lesson=lesson)


@bp.route('/lesson/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    """Delete a lesson"""
    require_admin()
    lesson = Lesson.query.get_or_404(lesson_id)
    portal_id = lesson.portal_id
    lesson_title = lesson.title
    
    db.session.delete(lesson)
    db.session.commit()
    
    flash(f'Lesson "{lesson_title}" deleted successfully!', 'success')
    return redirect(url_for('admin.portal_lessons', portal_id=portal_id))


# Quiz management routes
@bp.route('/lesson/<int:lesson_id>/quiz', methods=['GET', 'POST'])
@login_required
def manage_quiz(lesson_id):
    """Manage quiz for a lesson"""
    require_admin()
    lesson = Lesson.query.get_or_404(lesson_id)
    quiz = Quiz.query.filter_by(lesson_id=lesson_id).first()
    
    if request.method == 'POST':
        quiz_title = request.form.get('quiz_title', '').strip()
        if not quiz_title:
            flash('Quiz title is required.', 'error')
        else:
            if quiz:
                quiz.title = quiz_title
            else:
                quiz = Quiz(lesson_id=lesson_id, title=quiz_title)
                db.session.add(quiz)
            db.session.commit()
            flash('Quiz saved successfully!', 'success')
            return redirect(url_for('admin.manage_quiz', lesson_id=lesson_id))
    
    questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).order_by(QuizQuestion.order_index, QuizQuestion.id).all() if quiz else []
    
    return render_template('admin/quiz_form.html', lesson=lesson, quiz=quiz, questions=questions)


@bp.route('/quiz/<int:quiz_id>/question/add', methods=['POST'])
@login_required
def add_quiz_question(quiz_id):
    """Add a question to a quiz"""
    require_admin()
    quiz = Quiz.query.get_or_404(quiz_id)
    
    question_text = request.form.get('question_text', '').strip()
    option_a = request.form.get('option_a', '').strip()
    option_b = request.form.get('option_b', '').strip()
    option_c = request.form.get('option_c', '').strip()
    option_d = request.form.get('option_d', '').strip()
    correct_option = request.form.get('correct_option', 'A').upper()
    points = int(request.form.get('points', 1) or 1)
    order_index = int(request.form.get('order_index', 0) or 0)
    
    if not question_text or not option_a or not option_b:
        flash('Question text, option A, and option B are required.', 'error')
        return redirect(url_for('admin.manage_quiz', lesson_id=quiz.lesson_id))
    
    if correct_option not in ['A', 'B', 'C', 'D']:
        flash('Correct option must be A, B, C, or D.', 'error')
        return redirect(url_for('admin.manage_quiz', lesson_id=quiz.lesson_id))
    
    question = QuizQuestion(
        quiz_id=quiz_id,
        question_text=question_text,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c if option_c else None,
        option_d=option_d if option_d else None,
        correct_option=correct_option,
        points=points,
        order_index=order_index
    )
    db.session.add(question)
    db.session.flush()
    update_quiz_total_points(quiz_id)
    db.session.commit()
    
    flash('Question added successfully!', 'success')
    return redirect(url_for('admin.manage_quiz', lesson_id=quiz.lesson_id))


@bp.route('/quiz/question/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_quiz_question(question_id):
    """Delete a quiz question"""
    require_admin()
    question = QuizQuestion.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    lesson_id = Quiz.query.get_or_404(quiz_id).lesson_id
    
    db.session.delete(question)
    db.session.flush()
    update_quiz_total_points(quiz_id)
    db.session.commit()
    
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.manage_quiz', lesson_id=lesson_id))


# Task management routes
@bp.route('/lesson/<int:lesson_id>/task/add', methods=['POST'])
@login_required
def add_task(lesson_id):
    """Add a task to a lesson"""
    require_admin()
    lesson = Lesson.query.get_or_404(lesson_id)
    
    task_text = request.form.get('task_text', '').strip()
    points = int(request.form.get('points', 5) or 5)
    
    if not task_text:
        flash('Task text is required.', 'error')
        return redirect(url_for('admin.portal_lessons', portal_id=lesson.portal_id))
    
    task = Task(
        lesson_id=lesson_id,
        task_text=task_text,
        points=points,
        is_optional=False,
        order_index=0
    )
    db.session.add(task)
    db.session.commit()
    
    flash('Task added successfully!', 'success')
    return redirect(url_for('admin.portal_lessons', portal_id=lesson.portal_id))


@bp.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task"""
    require_admin()
    task = Task.query.get_or_404(task_id)
    portal_id = task.lesson.portal_id
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('admin.portal_lessons', portal_id=portal_id))


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
