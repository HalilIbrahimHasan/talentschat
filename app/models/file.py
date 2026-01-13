from datetime import datetime
from app.extensions import db


class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=True)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    mime = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Integer, nullable=False)  # bytes
    storage_key = db.Column(db.String(255), nullable=False)  # path to file
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    workspace = db.relationship('Workspace', back_populates='files')
    channel = db.relationship('Channel')
    uploader = db.relationship('User', back_populates='uploaded_files')
    
    def __repr__(self):
        return f'<File {self.filename}>'


class Snippet(db.Model):
    __tablename__ = 'snippets'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    language = db.Column(db.String(50), nullable=True)
    code = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    channel = db.relationship('Channel')
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<Snippet {self.id}>'




