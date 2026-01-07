from flask import render_template, redirect, url_for, flash, send_file, abort, request
from flask_login import login_required, current_user
from pathlib import Path
from app.blueprints.videos import bp
from app.models.workspace import Workspace
from app.models.video import Video, VideoLike, VideoComment, VideoStar
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
    
    # Get like counts, stars, and user's likes
    for video in videos:
        video.like_count = len(video.likes)
        video.user_liked = any(like.user_id == current_user.id for like in video.likes)
        # total_stars is a property, accessed directly in templates
        user_star = VideoStar.query.filter_by(
            video_id=video.id,
            user_id=current_user.id
        ).first()
        video.user_star_rating = user_star.stars if user_star else 0
    
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
    # total_stars is a property, accessed directly in templates
    video.user_star = VideoStar.query.filter_by(
        video_id=video_id,
        user_id=current_user.id
    ).first()
    video.user_star_rating = video.user_star.stars if video.user_star else 0
    video.comments_list = VideoComment.query.filter_by(video_id=video_id).order_by(VideoComment.created_at.asc()).all()
    video.can_delete = (video.uploader_id == current_user.id)
    
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


@bp.route('/v/<int:video_id>/delete', methods=['POST'])
@login_required
def delete(video_id):
    """Delete video (only by uploader)"""
    video = Video.query.get_or_404(video_id)
    
    if not can_view_workspace(current_user, video.workspace):
        abort(403)
    
    # Only the uploader can delete their own video
    if video.uploader_id != current_user.id:
        flash('You can only delete your own videos', 'error')
        return redirect(url_for('videos.feed', workspace_slug=video.workspace.slug))
    
    workspace_slug = video.workspace.slug
    
    # Delete physical file if it exists (not external URLs)
    if video.storage_key:
        video_path = Config.UPLOAD_FOLDER / video.storage_key
        if video_path.exists():
            try:
                video_path.unlink()
            except Exception as e:
                print(f"Error deleting video {video_path}: {e}")
    
    # Delete database record
    db.session.delete(video)
    db.session.commit()
    
    flash('Video deleted successfully', 'success')
    return redirect(url_for('videos.feed', workspace_slug=workspace_slug))

