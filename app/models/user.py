from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from sqlalchemy import func


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)  # Profile image path
    bio = db.Column(db.Text, nullable=True)  # User bio
    is_admin = db.Column(db.Boolean, default=False, nullable=False)  # Admin flag (only one admin allowed)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    workspace_memberships = db.relationship('WorkspaceMember', back_populates='user', cascade='all, delete-orphan')
    messages = db.relationship('Message', back_populates='user', cascade='all, delete-orphan')
    uploaded_files = db.relationship('File', back_populates='uploader', cascade='all, delete-orphan')
    uploaded_videos = db.relationship('Video', back_populates='uploader', cascade='all, delete-orphan')
    articles = db.relationship('Article', back_populates='author', cascade='all, delete-orphan')
    video_stars = db.relationship('VideoStar', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_published_articles_count(self):
        """Count of published articles"""
        from app.models.article import Article
        return Article.query.filter_by(author_id=self.id, is_published=True).count()
    
    def get_total_video_stars(self):
        """Total stars received on all videos"""
        from app.models.video import VideoStar, Video
        return db.session.query(func.sum(VideoStar.stars)).filter(
            VideoStar.video_id.in_(
                db.session.query(Video.id).filter_by(uploader_id=self.id)
            )
        ).scalar() or 0
    
    @property
    def published_articles_count(self):
        return self.get_published_articles_count()
    
    @property
    def total_video_stars(self):
        return self.get_total_video_stars()
    
    @property
    def has_gold_badge(self):
        """Check if user has gold badge (published 5+ articles)"""
        return self.published_articles_count >= 5
    
    def __repr__(self):
        return f'<User {self.email}>'

