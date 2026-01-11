"""API routes for learning features (quiz, tasks, comments, progress, lessons)"""
from flask import jsonify, request
from flask_login import login_required, current_user
from app.blueprints.api import bp
from app.models.learning import (
    Quiz, QuizQuestion, QuizSubmission, Task, TaskSubmission,
    StudentProgress, Lesson, Comment, CodingChallenge
)
from app.extensions import db
from app.services.scoring import recalculate_user_score
from datetime import datetime
import json


@bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    """Submit quiz answers and calculate score"""
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        data = request.get_json()
        answers = data.get('answers', {})
        
        # Calculate score
        questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
        score = 0
        total_points = 0
        
        for question in questions:
            total_points += question.points
            user_answer = answers.get(str(question.id), '').upper()
            if user_answer == question.correct_option.upper():
                score += question.points
        
        # Save or update submission
        submission = QuizSubmission.query.filter_by(
            user_id=current_user.id,
            quiz_id=quiz_id
        ).first()
        
        if submission:
            submission.score = score
            submission.answers_json = json.dumps(answers)
            submission.submitted_at = datetime.utcnow()
        else:
            submission = QuizSubmission(
                user_id=current_user.id,
                quiz_id=quiz_id,
                score=score,
                answers_json=json.dumps(answers)
            )
            db.session.add(submission)
        
        db.session.commit()
        
        # Recalculate user score for the portal
        lesson = quiz.lesson
        if lesson:
            recalculate_user_score(current_user.id, lesson.portal_id)
            recalculate_user_score(current_user.id, None)  # All portals
        
        return jsonify({
            'success': True,
            'score': score,
            'total_points': total_points,
            'percentage': round((score / total_points * 100) if total_points > 0 else 0, 1)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@bp.route('/task/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    """Toggle task completion"""
    try:
        task = Task.query.get_or_404(task_id)
        data = request.get_json()
        is_done = data.get('is_done', False)
        
        submission = TaskSubmission.query.filter_by(
            user_id=current_user.id,
            task_id=task_id
        ).first()
        
        if submission:
            submission.is_done = is_done
            submission.done_at = datetime.utcnow() if is_done else None
        else:
            submission = TaskSubmission(
                user_id=current_user.id,
                task_id=task_id,
                is_done=is_done,
                done_at=datetime.utcnow() if is_done else None
            )
            db.session.add(submission)
        
        db.session.commit()
        
        # Recalculate user score
        lesson = task.lesson
        if lesson:
            recalculate_user_score(current_user.id, lesson.portal_id)
            recalculate_user_score(current_user.id, None)
        
        return jsonify({'success': True, 'is_done': is_done})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@bp.route('/lesson/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    """Mark lesson as complete"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        progress = StudentProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        if not progress:
            progress = StudentProgress(
                user_id=current_user.id,
                lesson_id=lesson_id
            )
            db.session.add(progress)
        
        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
            db.session.commit()
            
            # Recalculate user score
            recalculate_user_score(current_user.id, lesson.portal_id)
            recalculate_user_score(current_user.id, None)
            
            return jsonify({
                'success': True,
                'points_earned': lesson.points_complete
            })
        else:
            return jsonify({'success': True, 'message': 'Already completed'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@bp.route('/progress/update', methods=['POST'])
@login_required
def update_progress():
    """Update video watch progress"""
    try:
        data = request.get_json()
        lesson_id = data.get('lesson_id')
        watched_seconds = data.get('watched_seconds', 0)
        
        if not lesson_id:
            return jsonify({'error': 'lesson_id required'}), 400
        
        progress = StudentProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        if not progress:
            progress = StudentProgress(
                user_id=current_user.id,
                lesson_id=lesson_id,
                watched_seconds=watched_seconds
            )
            db.session.add(progress)
        else:
            progress.watched_seconds = max(progress.watched_seconds, watched_seconds)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@bp.route('/comments', methods=['POST'])
@login_required
def add_comment():
    """Add a comment to a lesson or coding challenge"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        lesson_id = data.get('lesson_id')
        challenge_id = data.get('challenge_id')
        
        if not text:
            return jsonify({'error': 'Comment text required'}), 400
        
        if not lesson_id and not challenge_id:
            return jsonify({'error': 'lesson_id or challenge_id required'}), 400
        
        comment = Comment(
            user_id=current_user.id,
            lesson_id=lesson_id,
            challenge_id=challenge_id,
            text=text
        )
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'comment_id': comment.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

