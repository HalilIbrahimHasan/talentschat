from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.blueprints.articles import bp
from app.models.workspace import Workspace
from app.models.article import Article
from app.extensions import db
# Import Article model to ensure it's registered
import app.models.article
from app.services.permissions import can_view_workspace, can_manage_workspace
from datetime import datetime


def can_write_articles(user, workspace):
    """Check if user can write articles (owner/admin/author role)"""
    if not user or not workspace:
        return False
    from app.models.workspace import WorkspaceMember
    member = WorkspaceMember.query.filter_by(
        workspace_id=workspace.id,
        user_id=user.id
    ).first()
    if not member:
        return False
    # Allow owner, admin, and members (all members can be authors)
    return member.role in ('owner', 'admin', 'member')


@bp.route('')
@login_required
def list(workspace_slug):
    """List all articles in workspace"""
    workspace = Workspace.query.filter_by(slug=workspace_slug).first_or_404()
    
    if not can_view_workspace(current_user, workspace):
        abort(403)
    
    # Get published articles for all users, all articles for authors
    if can_write_articles(current_user, workspace):
        articles = Article.query.filter_by(workspace_id=workspace.id).order_by(Article.created_at.desc()).all()
    else:
        articles = Article.query.filter_by(workspace_id=workspace.id, is_published=True).order_by(Article.created_at.desc()).all()
    
    return render_template('article/list.html', workspace=workspace, articles=articles, can_write=can_write_articles(current_user, workspace))


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create(workspace_slug):
    """Create new article"""
    workspace = Workspace.query.filter_by(slug=workspace_slug).first_or_404()
    
    if not can_view_workspace(current_user, workspace):
        abort(403)
    
    if not can_write_articles(current_user, workspace):
        flash('You do not have permission to write articles', 'error')
        return redirect(url_for('articles.list', workspace_slug=workspace_slug))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        is_published = request.form.get('is_published') == 'on'
        
        if not title or not content:
            flash('Title and content are required', 'error')
            return render_template('article/create.html', workspace=workspace)
        
        article = Article(
            workspace_id=workspace.id,
            author_id=current_user.id,
            title=title,
            content=content,
            excerpt=excerpt
        )
        article.set_content_html()
        
        if is_published:
            article.publish()
        
        db.session.add(article)
        db.session.commit()
        
        flash('Article created successfully!', 'success')
        return redirect(url_for('articles.view', workspace_slug=workspace_slug, article_slug=article.slug))
    
    return render_template('article/create.html', workspace=workspace)


@bp.route('/<article_slug>')
@login_required
def view(workspace_slug, article_slug):
    """View article"""
    workspace = Workspace.query.filter_by(slug=workspace_slug).first_or_404()
    
    if not can_view_workspace(current_user, workspace):
        abort(403)
    
    article = Article.query.filter_by(
        workspace_id=workspace.id,
        slug=article_slug
    ).first_or_404()
    
    # Check if user can view (published or author)
    if not article.is_published and article.author_id != current_user.id:
        if not can_manage_workspace(current_user, workspace):
            abort(403)
    
    # Increment view count
    article.views_count += 1
    db.session.commit()
    
    can_edit = (article.author_id == current_user.id) or can_manage_workspace(current_user, workspace)
    
    return render_template('article/view.html', workspace=workspace, article=article, can_edit=can_edit)


@bp.route('/<article_slug>/edit', methods=['GET', 'POST'])
@login_required
def edit(workspace_slug, article_slug):
    """Edit article"""
    workspace = Workspace.query.filter_by(slug=workspace_slug).first_or_404()
    
    if not can_view_workspace(current_user, workspace):
        abort(403)
    
    article = Article.query.filter_by(
        workspace_id=workspace.id,
        slug=article_slug
    ).first_or_404()
    
    # Check permissions
    if article.author_id != current_user.id and not can_manage_workspace(current_user, workspace):
        flash('You do not have permission to edit this article', 'error')
        return redirect(url_for('articles.view', workspace_slug=workspace_slug, article_slug=article_slug))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        is_published = request.form.get('is_published') == 'on'
        
        if not title or not content:
            flash('Title and content are required', 'error')
            return render_template('article/edit.html', workspace=workspace, article=article)
        
        article.title = title
        article.content = content
        article.excerpt = excerpt
        article.set_content_html()
        article.updated_at = datetime.utcnow()
        
        if is_published and not article.is_published:
            article.publish()
        elif not is_published:
            article.is_published = False
        
        db.session.commit()
        
        flash('Article updated successfully!', 'success')
        return redirect(url_for('articles.view', workspace_slug=workspace_slug, article_slug=article.slug))
    
    return render_template('article/edit.html', workspace=workspace, article=article)


@bp.route('/<article_slug>/delete', methods=['POST'])
@login_required
def delete(workspace_slug, article_slug):
    """Delete article"""
    workspace = Workspace.query.filter_by(slug=workspace_slug).first_or_404()
    
    if not can_view_workspace(current_user, workspace):
        abort(403)
    
    article = Article.query.filter_by(
        workspace_id=workspace.id,
        slug=article_slug
    ).first_or_404()
    
    # Check permissions
    if article.author_id != current_user.id and not can_manage_workspace(current_user, workspace):
        flash('You do not have permission to delete this article', 'error')
        return redirect(url_for('articles.view', workspace_slug=workspace_slug, article_slug=article_slug))
    
    db.session.delete(article)
    db.session.commit()
    
    flash('Article deleted successfully', 'success')
    return redirect(url_for('articles.list', workspace_slug=workspace_slug))

