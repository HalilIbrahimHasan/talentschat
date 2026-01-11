"""Learning routes: Dashboard, Lesson Detail, Coding Challenge"""
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.blueprints.learn import bp
from app.models.learning import Portal, Lesson, Quiz, QuizQuestion, Task, CodingChallenge, StudentProgress, Comment, LeaderboardScore, CodingSubmission
from app.models.user import User
from app.extensions import db
from app.utils.youtube import extract_youtube_id, get_youtube_embed_url


@bp.route('')
@bp.route('/')
@login_required
def dashboard():
    """Learning dashboard - list all portals"""
    portals = Portal.query.order_by(Portal.id).all()
    return render_template('learn/dashboard.html', portals=portals)


@bp.route('/portal/<int:portal_id>/lessons')
@login_required
def lesson_list(portal_id):
    """List lessons in a portal"""
    portal = Portal.query.get_or_404(portal_id)
    lessons = Lesson.query.filter_by(portal_id=portal_id, is_active=True).order_by(Lesson.order_index, Lesson.id).all()
    
    # Get user progress for all lessons
    progress_map = {}
    progress_list = StudentProgress.query.filter_by(user_id=current_user.id).filter(
        StudentProgress.lesson_id.in_([l.id for l in lessons])
    ).all()
    for p in progress_list:
        progress_map[p.lesson_id] = p
    
    return render_template('learn/lesson_list.html', portal=portal, lessons=lessons, progress_map=progress_map)


@bp.route('/lesson/<int:lesson_id>')
@login_required
def lesson_detail(lesson_id):
    """Lesson detail page with video, quiz, tasks, comments"""
    lesson = Lesson.query.get_or_404(lesson_id)
    
    if not lesson.is_active:
        abort(404)
    
    # Get or create student progress
    progress = StudentProgress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if not progress:
        progress = StudentProgress(user_id=current_user.id, lesson_id=lesson_id)
        db.session.add(progress)
        db.session.commit()
    
    # Get quiz if exists
    quiz = Quiz.query.filter_by(lesson_id=lesson_id).first()
    quiz_questions = []
    if quiz:
        quiz_questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).order_by(QuizQuestion.order_index, QuizQuestion.id).all()
    
    # Get tasks
    tasks = Task.query.filter_by(lesson_id=lesson_id).order_by(Task.order_index, Task.id).all()
    
    # Get comments
    comments = Comment.query.filter_by(lesson_id=lesson_id).order_by(Comment.created_at.desc()).limit(50).all()
    
    # YouTube embed URL
    youtube_embed_url = None
    if lesson.youtube_id:
        youtube_embed_url = get_youtube_embed_url(lesson.youtube_id)
    
    return render_template(
        'learn/lesson_detail.html',
        lesson=lesson,
        progress=progress,
        quiz=quiz,
        quiz_questions=quiz_questions,
        tasks=tasks,
        comments=comments,
        youtube_embed_url=youtube_embed_url
    )


@bp.route('/code')
@login_required
def coding_challenges():
    """List all coding challenges"""
    difficulty = request.args.get('difficulty', '')
    
    query = CodingChallenge.query.filter_by(is_active=True)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    challenges = query.order_by(
        CodingChallenge.difficulty,
        CodingChallenge.id
    ).all()
    
    # Get completed challenge IDs for current user
    completed_submissions = CodingSubmission.query.filter_by(
        user_id=current_user.id,
        status='passed'
    ).all()
    completed_challenge_ids = {sub.challenge_id for sub in completed_submissions}
    
    return render_template(
        'learn/coding_challenges.html',
        challenges=challenges,
        current_difficulty=difficulty,
        completed_challenge_ids=completed_challenge_ids
    )


@bp.route('/code/<int:challenge_id>')
@login_required
def coding_challenge(challenge_id):
    """Coding challenge page with editor"""
    challenge = CodingChallenge.query.get_or_404(challenge_id)
    
    if not challenge.is_active:
        abort(404)
    
    # Get comments
    comments = Comment.query.filter_by(challenge_id=challenge_id).order_by(Comment.created_at.desc()).limit(50).all()
    
    # Parse test cases JSON
    import json
    try:
        test_cases = json.loads(challenge.test_cases_json) if challenge.test_cases_json else []
    except:
        test_cases = []
    
    return render_template(
        'learn/coding_challenge.html',
        challenge=challenge,
        comments=comments,
        test_cases=test_cases,
        starter_code=challenge.starter_code or ''
    )


@bp.route('/leaderboard')
@login_required
def leaderboard():
    """Leaderboard page"""
    from app.models.user import User
    
    portal_id = request.args.get('portal_id', type=int)
    range_filter = request.args.get('range', 'all')  # 'week', 'all'
    
    # Get portal if specified
    portal = None
    if portal_id:
        portal = Portal.query.get(portal_id)
    
    # Get all users and their scores
    all_users = User.query.all()
    user_scores = []
    
    for user in all_users:
        # Get score for this portal or all portals
        score_record = LeaderboardScore.query.filter_by(
            user_id=user.id,
            portal_id=portal_id if portal_id else None
        ).first()
        
        total_points = score_record.total_points if score_record else 0
        
        user_scores.append({
            'user': user,
            'portal': portal,
            'total_points': total_points,
            'score_record': score_record
        })
    
    # Sort by points descending
    user_scores.sort(key=lambda x: x['total_points'], reverse=True)
    
    # Limit to top 100
    user_scores = user_scores[:100]
    
    # Get all portals for filter dropdown
    portals = Portal.query.order_by(Portal.id).all()
    
    return render_template(
        'learn/leaderboard.html',
        user_scores=user_scores,
        portal=portal,
        portals=portals,
        current_portal_id=portal_id,
        current_range=range_filter
    )

