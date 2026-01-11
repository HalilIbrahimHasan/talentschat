"""Scoring and points calculation service"""
from datetime import datetime
from app.extensions import db
from app.models.learning import (
    LeaderboardScore, StudentProgress, QuizSubmission, 
    TaskSubmission, CodingSubmission, Lesson, Quiz, Task
)


def recalculate_user_score(user_id, portal_id=None):
    """
    Recalculate and update user's total points for a portal (or all portals).
    
    Args:
        user_id: User ID
        portal_id: Portal ID (None = all portals combined)
    
    Updates or creates LeaderboardScore record.
    """
    total_points = 0
    
    # Points from completed lessons
    if portal_id:
        lesson_completions = StudentProgress.query.filter_by(
            user_id=user_id,
            is_completed=True
        ).join(Lesson).filter(Lesson.portal_id == portal_id).all()
    else:
        lesson_completions = StudentProgress.query.filter_by(
            user_id=user_id,
            is_completed=True
        ).all()
    
    for progress in lesson_completions:
        total_points += progress.lesson.points_complete
    
    # Points from quiz submissions
    if portal_id:
        quiz_submissions = QuizSubmission.query.filter_by(
            user_id=user_id
        ).join(Quiz).join(Lesson).filter(Lesson.portal_id == portal_id).all()
    else:
        quiz_submissions = QuizSubmission.query.filter_by(user_id=user_id).all()
    
    for submission in quiz_submissions:
        total_points += submission.score
    
    # Points from task submissions
    if portal_id:
        task_submissions = TaskSubmission.query.filter_by(
            user_id=user_id,
            is_done=True
        ).join(Task).join(Lesson).filter(Lesson.portal_id == portal_id).all()
    else:
        task_submissions = TaskSubmission.query.filter_by(
            user_id=user_id,
            is_done=True
        ).all()
    
    for submission in task_submissions:
        total_points += submission.task.points
    
    # Points from coding submissions (passed)
    coding_submissions = CodingSubmission.query.filter_by(
        user_id=user_id,
        status='passed'
    ).all()
    
    # For coding challenges, only count the best submission per challenge
    challenge_best_scores = {}
    for submission in coding_submissions:
        if portal_id is None:  # All portals
            if submission.challenge_id not in challenge_best_scores:
                challenge_best_scores[submission.challenge_id] = submission.score
            else:
                challenge_best_scores[submission.challenge_id] = max(
                    challenge_best_scores[submission.challenge_id],
                    submission.score
                )
        # Note: Coding challenges don't have portal_id, so we include all if portal_id is None
        # If portal_id is set, we skip coding challenges (they're portal-agnostic)
    
    total_points += sum(challenge_best_scores.values())
    
    # Update or create LeaderboardScore
    score_record = LeaderboardScore.query.filter_by(
        user_id=user_id,
        portal_id=portal_id
    ).first()
    
    if score_record:
        score_record.total_points = total_points
        score_record.updated_at = datetime.utcnow()
    else:
        score_record = LeaderboardScore(
            user_id=user_id,
            portal_id=portal_id,
            total_points=total_points
        )
        db.session.add(score_record)
    
    db.session.commit()
    return total_points


def update_quiz_total_points(quiz_id):
    """Recalculate and update quiz.total_points from questions"""
    from app.models.learning import Quiz, QuizQuestion
    from sqlalchemy import func
    
    quiz = Quiz.query.get_or_404(quiz_id)
    total = db.session.query(func.sum(QuizQuestion.points)).filter_by(quiz_id=quiz_id).scalar() or 0
    quiz.total_points = total
    db.session.commit()
    return total

