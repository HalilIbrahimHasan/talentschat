from flask import render_template, redirect, url_for, flash, send_file, abort
from flask_login import login_required, current_user
from pathlib import Path
from app.blueprints.files import bp
from app.models.workspace import Workspace
from app.models.file import File, Snippet
from app.extensions import db
from app.services.permissions import can_view_workspace
from app.services.upload_service import save_uploaded_file, get_file_type, allowed_file
from app.config import Config


@bp.route('/docs')
@login_required
def docs(workspace_slug):
    """List all files and docs in workspace"""
    workspace = Workspace.query.filter_by(slug=workspace_slug).first_or_404()
    
    if not can_view_workspace(current_user, workspace):
        abort(403)
    
    files = File.query.filter_by(workspace_id=workspace.id).order_by(File.created_at.desc()).all()
    snippets = Snippet.query.join(Snippet.channel).filter(
        Snippet.channel.has(workspace_id=workspace.id)
    ).order_by(Snippet.created_at.desc()).all()
    
    return render_template('files/docs.html', workspace=workspace, files=files, snippets=snippets)


@bp.route('/<int:file_id>/download')
@login_required
def download(workspace_slug, file_id):
    """Download file"""
    workspace = Workspace.query.filter_by(slug=workspace_slug).first_or_404()
    
    if not can_view_workspace(current_user, workspace):
        abort(403)
    
    file = File.query.get_or_404(file_id)
    if file.workspace_id != workspace.id:
        abort(404)
    
    file_path = Config.UPLOAD_FOLDER / file.storage_key
    if not file_path.exists():
        abort(404)
    
    return send_file(str(file_path), as_attachment=True, download_name=file.filename)

