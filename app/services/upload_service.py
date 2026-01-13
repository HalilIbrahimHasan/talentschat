import os
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app
from app.config import Config


def allowed_file(filename, file_type='documents'):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = Config.ALLOWED_EXTENSIONS.get(file_type, set())
    return ext in allowed


def get_file_type(filename):
    """Determine file type from extension"""
    if '.' not in filename:
        return 'documents'
    ext = filename.rsplit('.', 1)[1].lower()
    
    if ext in Config.ALLOWED_EXTENSIONS['videos']:
        return 'videos'
    elif ext in Config.ALLOWED_EXTENSIONS['images']:
        return 'images'
    elif ext in Config.ALLOWED_EXTENSIONS['documents']:
        return 'documents'
    elif ext in Config.ALLOWED_EXTENSIONS['archives']:
        return 'archives'
    elif ext in Config.ALLOWED_EXTENSIONS['code']:
        return 'code'
    return 'documents'


def save_uploaded_file(file, file_type='documents', subfolder=''):
    """Save uploaded file and return storage path"""
    if not file or not file.filename:
        return None
    
    # Validate file
    if not allowed_file(file.filename, file_type):
        raise ValueError(f'File type not allowed: {file.filename}')
    
    # Secure filename
    filename = secure_filename(file.filename)
    
    # Create storage path
    if file_type == 'videos':
        storage_dir = Config.UPLOAD_FOLDER / 'videos' / subfolder
    else:
        storage_dir = Config.UPLOAD_FOLDER / 'files' / subfolder
    
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename if exists
    storage_path = storage_dir / filename
    counter = 1
    while storage_path.exists():
        name, ext = os.path.splitext(filename)
        storage_path = storage_dir / f'{name}_{counter}{ext}'
        counter += 1
    
    # Save file
    file.save(str(storage_path))
    
    # Return relative path from upload folder
    return storage_path.relative_to(Config.UPLOAD_FOLDER)


def delete_file(storage_key):
    """Delete file from storage"""
    file_path = Config.UPLOAD_FOLDER / storage_key
    if file_path.exists():
        file_path.unlink()
        return True
    return False




