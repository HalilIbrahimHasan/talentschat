from datetime import datetime
from app.extensions import db
from app.utils.ids import generate_slug


class Channel(db.Model):
    __tablename__ = 'channels'
    
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    is_private = db.Column(db.Boolean, default=False, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    workspace = db.relationship('Workspace', back_populates='channels')
    creator = db.relationship('User', foreign_keys=[created_by])
    members = db.relationship('ChannelMember', back_populates='channel', cascade='all, delete-orphan')
    messages = db.relationship('Message', back_populates='channel', cascade='all, delete-orphan', order_by='Message.created_at')
    pins = db.relationship('MessagePin', back_populates='channel', cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('workspace_id', 'slug', name='unique_channel_slug'),)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.slug:
            self.slug = generate_slug(self.name)
    
    def __repr__(self):
        return f'<Channel {self.name}>'


class ChannelMember(db.Model):
    __tablename__ = 'channel_members'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    channel = db.relationship('Channel', back_populates='members')
    user = db.relationship('User')
    
    __table_args__ = (db.UniqueConstraint('channel_id', 'user_id', name='unique_channel_member'),)
    
    def __repr__(self):
        return f'<ChannelMember {self.user_id} in {self.channel_id}>'




