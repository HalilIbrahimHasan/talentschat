import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
from app.blueprints.profile import bp
from app.models.user import User
from app.models.article import Article
from app.models.video import Video, VideoStar
from app.extensions import db
from app.blueprints.profile.forms import ProfileForm, ChangePasswordForm


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_profile_image(file):
    """Save profile image and return the filename"""
    # Check if file is a FileStorage object (has filename attribute)
    # If it's a string, it means no new file was uploaded
    if file and hasattr(file, 'filename') and file.filename:
        filename = secure_filename(file.filename)
        # Create unique filename
        ext = filename.rsplit('.', 1)[1].lower()
        filename = f"{current_user.id}_{current_user.email.split('@')[0]}.{ext}"
        
        upload_folder = current_app.config['UPLOAD_FOLDER'] / 'profiles'
        upload_folder.mkdir(exist_ok=True)
        
        filepath = upload_folder / filename
        
        # Resize image if needed
        try:
            img = Image.open(file)
            # Resize to max 400x400
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            img.save(filepath)
            return f"profiles/{filename}"
        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'error')
            return None
    return None


@bp.route('')
@bp.route('/')
@login_required
def view():
    """View own profile"""
    return redirect(url_for('profile.view_user', user_id=current_user.id))


@bp.route('/<int:user_id>')
@login_required
def view_user(user_id):
    """View any user's profile"""
    user = User.query.get_or_404(user_id)
    
    # Get user stats
    published_articles = Article.query.filter_by(author_id=user_id, is_published=True).count()
    total_stars = user.get_total_video_stars()
    videos_count = Video.query.filter_by(uploader_id=user_id).count()
    
    # Get recent articles
    recent_articles = Article.query.filter_by(
        author_id=user_id, 
        is_published=True
    ).order_by(Article.created_at.desc()).limit(5).all()
    
    # Get recent videos
    recent_videos = Video.query.filter_by(uploader_id=user_id).order_by(
        Video.created_at.desc()
    ).limit(5).all()
    
    return render_template('profile/view.html',
                         user=user,
                         published_articles=published_articles,
                         total_stars=total_stars,
                         videos_count=videos_count,
                         recent_articles=recent_articles,
                         recent_videos=recent_videos)


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit own profile"""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        
        # Handle profile image upload
        if form.profile_image.data:
            image_path = save_profile_image(form.profile_image.data)
            if image_path:
                # Delete old profile image if exists
                if current_user.profile_image:
                    old_path = current_app.config['UPLOAD_FOLDER'] / current_user.profile_image
                    if old_path.exists():
                        old_path.unlink()
                current_user.profile_image = image_path
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.view'))
    
    return render_template('profile/edit.html', form=form)


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect', 'error')
            return render_template('profile/change_password.html', form=form)
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile.view'))
    
    return render_template('profile/change_password.html', form=form)


@bp.route('/image/<path:filename>')
@login_required
def serve_image(filename):
    """Serve profile images"""
    from flask import send_from_directory
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(str(upload_folder), filename)

