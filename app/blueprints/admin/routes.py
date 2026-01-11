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


@bp.route('/learn')
@login_required
def learn_dashboard():
    """Admin dashboard for learning content"""
    require_admin()
    portals = Portal.query.order_by(Portal.id).all()
    challenges = CodingChallenge.query.order_by(CodingChallenge.id).all()
    return render_template('admin/learn_dashboard.html', portals=portals, challenges=challenges)


# Portal Management
@bp.route('/learn/portals/create', methods=['GET', 'POST'])
@login_required
def create_portal():
    """Create a new portal"""
    require_admin()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Portal name is required', 'error')
            return render_template('admin/portal_form.html')
        
        portal = Portal(name=name, description=description or None)
        db.session.add(portal)
        db.session.commit()
        flash('Portal created successfully!', 'success')
        return redirect(url_for('admin.learn_dashboard'))
    
    return render_template('admin/portal_form.html')


@bp.route('/learn/portals/<int:portal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_portal(portal_id):
    """Edit a portal"""
    require_admin()
    portal = Portal.query.get_or_404(portal_id)
    
    if request.method == 'POST':
        portal.name = request.form.get('name', '').strip()
        portal.description = request.form.get('description', '').strip() or None
        db.session.commit()
        flash('Portal updated successfully!', 'success')
        return redirect(url_for('admin.learn_dashboard'))
    
    return render_template('admin/portal_form.html', portal=portal)


@bp.route('/learn/portals/<int:portal_id>/delete', methods=['POST'])
@login_required
def delete_portal(portal_id):
    """Delete a portal"""
    require_admin()
    portal = Portal.query.get_or_404(portal_id)
    db.session.delete(portal)
    db.session.commit()
    flash('Portal deleted successfully!', 'success')
    return redirect(url_for('admin.learn_dashboard'))


# Lesson Management
@bp.route('/learn/portals/<int:portal_id>/lessons/create', methods=['GET', 'POST'])
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
            flash('Lesson title is required', 'error')
            return render_template('admin/lesson_form.html', portal=portal)
        
        youtube_id = extract_youtube_id(youtube_url) if youtube_url else None
        
        lesson = Lesson(
            portal_id=portal_id,
            title=title,
            description=description or None,
            youtube_url=youtube_url or None,
            youtube_id=youtube_id,
            points_complete=points_complete,
            order_index=order_index
        )
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('admin.portal_lessons', portal_id=portal_id))
    
    return render_template('admin/lesson_form.html', portal=portal)


@bp.route('/learn/portals/<int:portal_id>/lessons')
@login_required
def portal_lessons(portal_id):
    """List lessons in a portal"""
    require_admin()
    portal = Portal.query.get_or_404(portal_id)
    lessons = Lesson.query.filter_by(portal_id=portal_id).order_by(Lesson.order_index, Lesson.id).all()
    return render_template('admin/portal_lessons.html', portal=portal, lessons=lessons)


@bp.route('/learn/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    """Edit a lesson"""
    require_admin()
    lesson = Lesson.query.get_or_404(lesson_id)
    
    if request.method == 'POST':
        lesson.title = request.form.get('title', '').strip()
        lesson.description = request.form.get('description', '').strip() or None
        youtube_url = request.form.get('youtube_url', '').strip()
        lesson.youtube_url = youtube_url or None
        lesson.youtube_id = extract_youtube_id(youtube_url) if youtube_url else None
        lesson.points_complete = int(request.form.get('points_complete', 10) or 10)
        lesson.order_index = int(request.form.get('order_index', 0) or 0)
        db.session.commit()
        flash('Lesson updated successfully!', 'success')
        return redirect(url_for('admin.portal_lessons', portal_id=lesson.portal_id))
    
    return render_template('admin/lesson_form.html', portal=lesson.portal, lesson=lesson)


@bp.route('/learn/lessons/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    """Delete a lesson"""
    require_admin()
    lesson = Lesson.query.get_or_404(lesson_id)
    portal_id = lesson.portal_id
    db.session.delete(lesson)
    db.session.commit()
    flash('Lesson deleted successfully!', 'success')
    return redirect(url_for('admin.portal_lessons', portal_id=portal_id))


# Quiz Management
@bp.route('/learn/lessons/<int:lesson_id>/quiz', methods=['GET', 'POST'])
@login_required
def manage_quiz(lesson_id):
    """Create or edit quiz for a lesson"""
    require_admin()
    lesson = Lesson.query.get_or_404(lesson_id)
    quiz = Quiz.query.filter_by(lesson_id=lesson_id).first()
    questions = []
    if quiz:
        questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).order_by(QuizQuestion.order_index, QuizQuestion.id).all()
    
    if request.method == 'POST':
        title = request.form.get('quiz_title', '').strip()
        if not title:
            flash('Quiz title is required', 'error')
            return render_template('admin/quiz_form.html', lesson=lesson, quiz=quiz, questions=questions)
        
        if not quiz:
            quiz = Quiz(lesson_id=lesson_id, title=title)
            db.session.add(quiz)
            db.session.commit()
        else:
            quiz.title = title
            db.session.commit()
        
        flash('Quiz saved successfully!', 'success')
        return redirect(url_for('admin.manage_quiz', lesson_id=lesson_id))
    
    return render_template('admin/quiz_form.html', lesson=lesson, quiz=quiz, questions=questions)


@bp.route('/learn/quizzes/<int:quiz_id>/questions/add', methods=['POST'])
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
    correct_option = request.form.get('correct_option', 'A').strip().upper()
    points = int(request.form.get('points', 1) or 1)
    order_index = int(request.form.get('order_index', 0) or 0)
    
    if not question_text or not option_a or not option_b:
        flash('Question text and at least two options are required', 'error')
        return redirect(url_for('admin.manage_quiz', lesson_id=quiz.lesson_id))
    
    question = QuizQuestion(
        quiz_id=quiz_id,
        question_text=question_text,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c or None,
        option_d=option_d or None,
        correct_option=correct_option,
        points=points,
        order_index=order_index
    )
    db.session.add(question)
    db.session.commit()
    update_quiz_total_points(quiz_id)
    flash('Question added successfully!', 'success')
    return redirect(url_for('admin.manage_quiz', lesson_id=quiz.lesson_id))


@bp.route('/learn/quizzes/questions/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_quiz_question(question_id):
    """Delete a quiz question"""
    require_admin()
    question = QuizQuestion.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    lesson_id = Quiz.query.get(quiz_id).lesson_id
    db.session.delete(question)
    db.session.commit()
    update_quiz_total_points(quiz_id)
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.manage_quiz', lesson_id=lesson_id))


# Task Management
@bp.route('/learn/lessons/<int:lesson_id>/tasks/add', methods=['POST'])
@login_required
def add_task(lesson_id):
    """Add a task to a lesson"""
    require_admin()
    lesson = Lesson.query.get_or_404(lesson_id)
    
    task_text = request.form.get('task_text', '').strip()
    points = int(request.form.get('points', 5) or 5)
    is_optional = request.form.get('is_optional') == 'on'
    order_index = int(request.form.get('order_index', 0) or 0)
    
    if not task_text:
        flash('Task text is required', 'error')
        return redirect(url_for('admin.portal_lessons', portal_id=lesson.portal_id))
    
    task = Task(
        lesson_id=lesson_id,
        task_text=task_text,
        points=points,
        is_optional=is_optional,
        order_index=order_index
    )
    db.session.add(task)
    db.session.commit()
    flash('Task added successfully!', 'success')
    return redirect(url_for('admin.portal_lessons', portal_id=lesson.portal_id))


@bp.route('/learn/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task"""
    require_admin()
    task = Task.query.get_or_404(task_id)
    lesson = task.lesson
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('admin.portal_lessons', portal_id=lesson.portal_id))


# Coding Challenge Management
@bp.route('/learn/coding/create', methods=['GET', 'POST'])
@login_required
def create_coding_challenge():
    """Create a coding challenge"""
    require_admin()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        difficulty = request.form.get('difficulty', 'easy').strip()
        starter_code = request.form.get('starter_code', '').strip()
        test_cases_json = request.form.get('test_cases_json', '').strip()
        points = int(request.form.get('points', 20) or 20)
        
        if not title or not description:
            flash('Title and description are required', 'error')
            return render_template('admin/coding_challenge_form.html')
        
        # Validate JSON
        try:
            if test_cases_json:
                json.loads(test_cases_json)
        except:
            flash('Invalid JSON format for test cases', 'error')
            return render_template('admin/coding_challenge_form.html')
        
        challenge = CodingChallenge(
            title=title,
            description=description,
            difficulty=difficulty,
            starter_code=starter_code or None,
            test_cases_json=test_cases_json or '[]',
            points=points
        )
        db.session.add(challenge)
        db.session.commit()
        flash('Coding challenge created successfully!', 'success')
        return redirect(url_for('admin.learn_dashboard'))
    
    return render_template('admin/coding_challenge_form.html')


@bp.route('/learn/coding/<int:challenge_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_coding_challenge(challenge_id):
    """Edit a coding challenge"""
    require_admin()
    challenge = CodingChallenge.query.get_or_404(challenge_id)
    
    if request.method == 'POST':
        challenge.title = request.form.get('title', '').strip()
        challenge.description = request.form.get('description', '').strip()
        challenge.difficulty = request.form.get('difficulty', 'easy').strip()
        challenge.starter_code = request.form.get('starter_code', '').strip() or None
        test_cases_json = request.form.get('test_cases_json', '').strip()
        challenge.points = int(request.form.get('points', 20) or 20)
        
        # Validate JSON
        try:
            if test_cases_json:
                json.loads(test_cases_json)
            challenge.test_cases_json = test_cases_json or '[]'
        except:
            flash('Invalid JSON format for test cases', 'error')
            return render_template('admin/coding_challenge_form.html', challenge=challenge)
        
        db.session.commit()
        flash('Coding challenge updated successfully!', 'success')
        return redirect(url_for('admin.learn_dashboard'))
    
    return render_template('admin/coding_challenge_form.html', challenge=challenge)


@bp.route('/learn/coding/<int:challenge_id>/delete', methods=['POST'])
@login_required
def delete_coding_challenge(challenge_id):
    """Delete a coding challenge"""
    require_admin()
    challenge = CodingChallenge.query.get_or_404(challenge_id)
    db.session.delete(challenge)
    db.session.commit()
    flash('Coding challenge deleted successfully!', 'success')
    return redirect(url_for('admin.learn_dashboard'))

