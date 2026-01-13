from datetime import datetime
from app.extensions import db
import bleach


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    edited_at = db.Column(db.DateTime, nullable=True)
    reply_to_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=True)
    
    # Relationships
    channel = db.relationship('Channel', back_populates='messages')
    user = db.relationship('User', back_populates='messages')
    reply_to = db.relationship('Message', remote_side=[id], backref='replies')
    reactions = db.relationship('MessageReaction', back_populates='message', cascade='all, delete-orphan')
    highlights = db.relationship('MessageHighlight', back_populates='message', cascade='all, delete-orphan')
    
    def set_content_html(self):
        """Sanitize and convert content to HTML"""
        allowed_tags = ['b', 'i', 'u', 'strong', 'em', 'a', 'code', 'pre', 'br', 'p']
        allowed_attrs = {'a': ['href', 'title']}
        self.content_html = bleach.clean(
            self.content.replace('\n', '<br>'),
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
    
    def __repr__(self):
        return f'<Message {self.id} by {self.user_id}>'


class MessageReaction(db.Model):
    __tablename__ = 'message_reactions'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    emoji = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    message = db.relationship('Message', back_populates='reactions')
    user = db.relationship('User')
    
    __table_args__ = (db.UniqueConstraint('message_id', 'user_id', 'emoji', name='unique_reaction'),)
    
    def __repr__(self):
        return f'<MessageReaction {self.emoji} on {self.message_id}>'


class MessageHighlight(db.Model):
    __tablename__ = 'message_highlights'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    highlighted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    message = db.relationship('Message', back_populates='highlights')
    user = db.relationship('User', foreign_keys=[highlighted_by])
    
    __table_args__ = (db.UniqueConstraint('message_id', 'highlighted_by', name='unique_highlight'),)
    
    def __repr__(self):
        return f'<MessageHighlight {self.message_id} by {self.highlighted_by}>'


class MessagePin(db.Model):
    __tablename__ = 'message_pins'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    pinned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    channel = db.relationship('Channel', back_populates='pins')
    message = db.relationship('Message')
    user = db.relationship('User', foreign_keys=[pinned_by])
    
    def __repr__(self):
        return f'<MessagePin {self.message_id} in {self.channel_id}>'




