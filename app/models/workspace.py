from datetime import datetime
from app.extensions import db
from app.utils.ids import generate_slug


class Workspace(db.Model):
    __tablename__ = 'workspaces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=True, nullable=False)  # Public workspaces can be discovered
    invite_code = db.Column(db.String(20), unique=True, nullable=True, index=True)  # Optional invite code
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = db.relationship('User', foreign_keys=[owner_id])
    members = db.relationship('WorkspaceMember', back_populates='workspace', cascade='all, delete-orphan')
    channels = db.relationship('Channel', back_populates='workspace', cascade='all, delete-orphan')
    files = db.relationship('File', back_populates='workspace', cascade='all, delete-orphan')
    videos = db.relationship('Video', back_populates='workspace', cascade='all, delete-orphan')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.slug:
            self.slug = generate_slug(self.name)
        if not self.invite_code:
            from app.utils.ids import generate_invite_code
            self.invite_code = generate_invite_code()
    
    def __repr__(self):
        return f'<Workspace {self.name}>'


class WorkspaceMember(db.Model):
    __tablename__ = 'workspace_members'
    
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member', nullable=False)  # owner, admin, member, guest
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    workspace = db.relationship('Workspace', back_populates='members')
    user = db.relationship('User', back_populates='workspace_memberships')
    
    __table_args__ = (db.UniqueConstraint('workspace_id', 'user_id', name='unique_workspace_member'),)
    
    def __repr__(self):
        return f'<WorkspaceMember {self.user_id} in {self.workspace_id}>'

