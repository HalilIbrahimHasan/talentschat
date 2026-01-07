from datetime import datetime
from app.extensions import db


class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    storage_key = db.Column(db.String(255), nullable=True)  # path to file (nullable for external URLs)
    external_url = db.Column(db.String(500), nullable=True)  # For social media links (YouTube, Vimeo, etc.)
    video_type = db.Column(db.String(20), default='upload', nullable=False)  # 'upload', 'recording', 'screen_share', 'external'
    duration = db.Column(db.Integer, nullable=True)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    workspace = db.relationship('Workspace', back_populates='videos')
    channel = db.relationship('Channel')
    uploader = db.relationship('User', back_populates='uploaded_videos')
    likes = db.relationship('VideoLike', back_populates='video', cascade='all, delete-orphan')
    comments = db.relationship('VideoComment', back_populates='video', cascade='all, delete-orphan', order_by='VideoComment.created_at')
    
    def __repr__(self):
        return f'<Video {self.id}>'


class VideoLike(db.Model):
    __tablename__ = 'video_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    video = db.relationship('Video', back_populates='likes')
    user = db.relationship('User')
    
    __table_args__ = (db.UniqueConstraint('video_id', 'user_id', name='unique_video_like'),)
    
    def __repr__(self):
        return f'<VideoLike {self.video_id} by {self.user_id}>'


class VideoComment(db.Model):
    __tablename__ = 'video_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    video = db.relationship('Video', back_populates='comments')
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<VideoComment {self.id}>'

