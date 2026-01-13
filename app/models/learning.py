"""Learning module models: Portals, Lessons, Quizzes, Tasks, Coding Challenges, Progress, etc."""
from datetime import datetime
from app.extensions import db


class Portal(db.Model):
    """Learning portals (Fun Videos, Installation Videos, Courses)"""
    __tablename__ = 'portals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    lessons = db.relationship('Lesson', back_populates='portal', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Portal {self.name}>'


class Lesson(db.Model):
    """Lessons within portals"""
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    portal_id = db.Column(db.Integer, db.ForeignKey('portals.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    youtube_url = db.Column(db.String(500), nullable=True)
    youtube_id = db.Column(db.String(50), nullable=True)  # Parsed YouTube ID
    points_complete = db.Column(db.Integer, default=10, nullable=False)
    order_index = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    portal = db.relationship('Portal', back_populates='lessons')
    quiz = db.relationship('Quiz', back_populates='lesson', uselist=False, cascade='all, delete-orphan')
    tasks = db.relationship('Task', back_populates='lesson', lazy='dynamic', cascade='all, delete-orphan', order_by='Task.id')
    progress = db.relationship('StudentProgress', back_populates='lesson', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='lesson', lazy='dynamic', cascade='all, delete-orphan', order_by='Comment.created_at.desc()')
    
    def __repr__(self):
        return f'<Lesson {self.title}>'


class Quiz(db.Model):
    """Quiz for a lesson"""
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=False)
    total_points = db.Column(db.Integer, default=0, nullable=False)  # Calculated from questions
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    lesson = db.relationship('Lesson', back_populates='quiz')
    questions = db.relationship('QuizQuestion', back_populates='quiz', lazy='dynamic', cascade='all, delete-orphan', order_by='QuizQuestion.id')
    submissions = db.relationship('QuizSubmission', back_populates='quiz', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Quiz {self.title}>'


class QuizQuestion(db.Model):
    """Individual quiz questions (MCQ)"""
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=True)
    option_d = db.Column(db.String(500), nullable=True)
    correct_option = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', or 'D'
    points = db.Column(db.Integer, default=1, nullable=False)
    order_index = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    quiz = db.relationship('Quiz', back_populates='questions')
    
    def __repr__(self):
        return f'<QuizQuestion {self.id}>'


class Task(db.Model):
    """Tasks/checklist items for lessons"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False)
    task_text = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, default=5, nullable=False)
    is_optional = db.Column(db.Boolean, default=False, nullable=False)
    order_index = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    lesson = db.relationship('Lesson', back_populates='tasks')
    submissions = db.relationship('TaskSubmission', back_populates='task', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Task {self.id}>'


class CodingChallenge(db.Model):
    """Python coding challenges"""
    __tablename__ = 'coding_challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='easy', nullable=False)  # easy, medium, hard
    starter_code = db.Column(db.Text, nullable=True)
    test_cases_json = db.Column(db.Text, nullable=False)  # JSON string of test cases
    points = db.Column(db.Integer, default=20, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    submissions = db.relationship('CodingSubmission', back_populates='challenge', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='challenge', lazy='dynamic', cascade='all, delete-orphan', order_by='Comment.created_at.desc()')
    
    def __repr__(self):
        return f'<CodingChallenge {self.title}>'


class StudentProgress(db.Model):
    """Student progress on lessons (video watch time, completion)"""
    __tablename__ = 'student_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False)
    watched_seconds = db.Column(db.Integer, default=0, nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='lesson_progress')
    lesson = db.relationship('Lesson', back_populates='progress')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson_progress'),)
    
    def __repr__(self):
        return f'<StudentProgress user={self.user_id} lesson={self.lesson_id}>'


class QuizSubmission(db.Model):
    """Student quiz submissions"""
    __tablename__ = 'quiz_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer, default=0, nullable=False)
    answers_json = db.Column(db.Text, nullable=False)  # JSON: {question_id: "A"}
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='quiz_submissions')
    quiz = db.relationship('Quiz', back_populates='submissions')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'quiz_id', name='unique_user_quiz_submission'),)
    
    def __repr__(self):
        return f'<QuizSubmission user={self.user_id} quiz={self.quiz_id} score={self.score}>'


class TaskSubmission(db.Model):
    """Student task completions"""
    __tablename__ = 'task_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    is_done = db.Column(db.Boolean, default=False, nullable=False)
    done_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='task_submissions')
    task = db.relationship('Task', back_populates='submissions')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'task_id', name='unique_user_task_submission'),)
    
    def __repr__(self):
        return f'<TaskSubmission user={self.user_id} task={self.task_id}>'


class CodingSubmission(db.Model):
    """Student coding challenge submissions"""
    __tablename__ = 'coding_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('coding_challenges.id', ondelete='CASCADE'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'passed', 'failed', 'error'
    score = db.Column(db.Integer, default=0, nullable=False)
    runtime_ms = db.Column(db.Integer, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    test_results_json = db.Column(db.Text, nullable=True)  # JSON: test case results
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='coding_submissions')
    challenge = db.relationship('CodingChallenge', back_populates='submissions')
    
    def __repr__(self):
        return f'<CodingSubmission user={self.user_id} challenge={self.challenge_id} status={self.status}>'


class LeaderboardScore(db.Model):
    """Cached leaderboard scores (updated on score changes)"""
    __tablename__ = 'leaderboard_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    portal_id = db.Column(db.Integer, db.ForeignKey('portals.id', ondelete='CASCADE'), nullable=True)  # NULL = all portals
    total_points = db.Column(db.Integer, default=0, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='leaderboard_scores')
    portal = db.relationship('Portal', backref='leaderboard_scores')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'portal_id', name='unique_user_portal_score'),)
    
    def __repr__(self):
        return f'<LeaderboardScore user={self.user_id} portal={self.portal_id} points={self.total_points}>'


class Comment(db.Model):
    """Comments on lessons or coding challenges"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('coding_challenges.id', ondelete='CASCADE'), nullable=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='comments')
    lesson = db.relationship('Lesson', back_populates='comments')
    challenge = db.relationship('CodingChallenge', back_populates='comments')
    
    __table_args__ = (db.CheckConstraint('(lesson_id IS NOT NULL AND challenge_id IS NULL) OR (lesson_id IS NULL AND challenge_id IS NOT NULL)', name='comment_has_one_target'),)
    
    def __repr__(self):
        return f'<Comment {self.id}>'




