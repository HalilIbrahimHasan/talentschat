import os
from pathlib import Path

basedir = Path(__file__).parent.parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLite-only (Postgres disabled)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{basedir / "app.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Note: SQLALCHEMY_ENGINE_OPTIONS is set dynamically in app/__init__.py
    # based on database type for eventlet compatibility
    
    # Upload settings
    UPLOAD_FOLDER = basedir / 'uploads'
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB max file size
    ALLOWED_EXTENSIONS = {
        'images': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
        'documents': {'pdf', 'doc', 'docx', 'txt', 'md'},
        'videos': {'mp4', 'webm', 'mov'},
        'archives': {'zip', 'rar', '7z'},
        'code': {'py', 'js', 'html', 'css', 'json', 'xml', 'txt'}
    }
    
    # File size limits
    MAX_DOC_SIZE = 20 * 1024 * 1024  # 20MB
    MAX_VIDEO_SIZE = 200 * 1024 * 1024  # 200MB
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Create upload directories
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    (UPLOAD_FOLDER / 'files').mkdir(exist_ok=True)
    (UPLOAD_FOLDER / 'videos').mkdir(exist_ok=True)
    (UPLOAD_FOLDER / 'avatars').mkdir(exist_ok=True)
    (UPLOAD_FOLDER / 'profiles').mkdir(exist_ok=True)

