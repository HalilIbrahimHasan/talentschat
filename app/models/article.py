from datetime import datetime
from app.extensions import db
from app.utils.ids import generate_slug
import bleach


class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text, nullable=True)  # Rendered HTML
    excerpt = db.Column(db.String(500), nullable=True)  # Short summary
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    published_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    views_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Relationships
    workspace = db.relationship('Workspace', back_populates='articles')
    author = db.relationship('User', back_populates='articles')
    
    __table_args__ = (db.UniqueConstraint('workspace_id', 'slug', name='unique_article_slug'),)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.slug and self.title:
            self.slug = generate_slug(self.title)
    
    def set_content_html(self):
        """Convert markdown/content to HTML"""
        # Allow more HTML tags for rich content
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img',
            'div', 'span', 'table', 'thead', 'tbody', 'tr', 'td', 'th'
        ]
        allowed_attrs = {
            'a': ['href', 'title', 'target'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'div': ['class'],
            'span': ['class'],
            'code': ['class']
        }
        
        # Basic markdown-like conversion
        html = self.content
        
        # Convert newlines to <br>
        html = html.replace('\n\n', '</p><p>')
        html = html.replace('\n', '<br>')
        
        # Headers
        html = html.replace('### ', '<h3>').replace('\n', '</h3>')
        html = html.replace('## ', '<h2>').replace('\n', '</h2>')
        html = html.replace('# ', '<h1>').replace('\n', '</h1>')
        
        # Bold and italic
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        html = html.replace('*', '<em>').replace('*', '</em>')
        
        # Wrap in paragraph if not already wrapped
        if not html.startswith('<'):
            html = f'<p>{html}</p>'
        
        # Sanitize
        self.content_html = bleach.clean(
            html,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
    
    def publish(self):
        """Publish the article"""
        self.is_published = True
        if not self.published_at:
            self.published_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Article {self.title}>'

