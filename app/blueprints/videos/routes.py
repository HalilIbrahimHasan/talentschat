from flask import render_template, redirect, url_for, flash, send_file, abort, request
from flask_login import login_required, current_user
from pathlib import Path
from app.blueprints.videos import bp
from app.models.workspace import Workspace
from app.models.video import Video, VideoLike, VideoComment
from app.extensions import db
from app.services.permissions import can_view_workspace
from app.config import Config


@bp.route('/w/<workspace_slug>/videos')
@login_required
def feed(workspace_slug):
    """Video feed for workspace"""
    workspace = Workspace.query.filter_by(slug=workspace_slug).first_or_404()
    
    if not can_view_workspace(current_user, workspace):
        abort(403)
    
    videos = Video.query.filter_by(workspace_id=workspace.id).order_by(Video.created_at.desc()).all()
    
    # Get like counts and user's likes
    for video in videos:
        video.like_count = len(video.likes)
        video.user_liked = any(like.user_id == current_user.id for like in video.likes)
    
    return render_template('video/feed.html', workspace=workspace, videos=videos)


@bp.route('/v/<int:video_id>')
@login_required
def view(video_id):
    """Video detail page with comments and likes"""
    video = Video.query.get_or_404(video_id)
    
    if not can_view_workspace(current_user, video.workspace):
        abort(403)
    
    video.like_count = len(video.likes)
    video.user_liked = any(like.user_id == current_user.id for like in video.likes)
    video.comments_list = VideoComment.query.filter_by(video_id=video_id).order_by(VideoComment.created_at.asc()).all()
    
    return render_template('video/view.html', video=video)


@bp.route('/v/<int:video_id>/stream')
@login_required
def stream(video_id):
    """Stream video file with range support"""
    video = Video.query.get_or_404(video_id)
    
    if not can_view_workspace(current_user, video.workspace):
        abort(403)
    
    video_path = Config.UPLOAD_FOLDER / video.storage_key
    if not video_path.exists():
        abort(404)
    
    return send_file(str(video_path), mimetype='video/mp4')

