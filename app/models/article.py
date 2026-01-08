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
            base_slug = generate_slug(self.title)
            # Ensure slug is unique within workspace
            if self.workspace_id:
                self.slug = self._make_unique_slug(base_slug)
            else:
                self.slug = base_slug
    
    def _make_unique_slug(self, base_slug):
        """Generate a unique slug by appending a number if needed"""
        slug = base_slug
        counter = 1
        while Article.query.filter_by(workspace_id=self.workspace_id, slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug
    
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
        if not self.content or not self.content.strip():
            self.content_html = '<p></p>'
            return
            
        html = self.content
        
        # Convert headers first (before other processing)
        import re
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Convert bold text **text** to <strong>text</strong>
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Convert italic text *text* to <em>text</em> (but not if already in strong)
        html = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<em>\1</em>', html)
        
        # Split by double newlines for paragraphs, but preserve existing HTML tags
        # Only split if the line doesn't start with an HTML tag
        lines = html.split('\n')
        paragraphs = []
        current_para = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_para:
                    paragraphs.append(' '.join(current_para))
                    current_para = []
            elif line.startswith('<'):
                # Already HTML, add as-is
                if current_para:
                    paragraphs.append(' '.join(current_para))
                    current_para = []
                paragraphs.append(line)
            else:
                current_para.append(line)
        
        if current_para:
            paragraphs.append(' '.join(current_para))
        
        # Join paragraphs with </p><p> tags
        if paragraphs:
            html = '</p><p>'.join(paragraphs)
            # Wrap in paragraph tags
            if not html.startswith('<'):
                html = f'<p>{html}</p>'
        else:
            html = f'<p>{html}</p>'
        
        # Convert remaining single newlines within paragraphs to <br>
        # But avoid breaking HTML tags
        html = re.sub(r'(?<!>)\n(?!<)', '<br>', html)
        
        # Sanitize - but don't strip, just clean
        self.content_html = bleach.clean(
            html,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=False  # Don't strip, just clean
        )
    
    def publish(self):
        """Publish the article"""
        self.is_published = True
        if not self.published_at:
            self.published_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Article {self.title}>'

