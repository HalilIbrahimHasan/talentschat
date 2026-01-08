from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.blueprints.articles import bp
from app.models.workspace import Workspace
from app.models.article import Article
from app.extensions import db
# Import Article model to ensure it's registered
import app.models.article
from app.services.permissions import can_view_workspace, can_manage_workspace
from app.blueprints.articles.forms import ArticleForm
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
    
    # Get articles user can view:
    # - Published articles: all users can view
    # - Draft articles: only author or workspace managers can view
    if can_write_articles(current_user, workspace):
        # Authors can see all articles (their own drafts + all published)
        from sqlalchemy import or_
        articles = Article.query.filter(
            Article.workspace_id == workspace.id,
            or_(
                Article.is_published == True,
                Article.author_id == current_user.id
            )
        ).order_by(Article.created_at.desc()).all()
    else:
        # Non-authors can only see published articles
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
    
    form = ArticleForm()
    
    if form.validate_on_submit():
        # Create article with workspace_id first so slug generation can check for uniqueness
        article = Article(
            workspace_id=workspace.id,
            author_id=current_user.id,
            title=form.title.data.strip(),
            content=form.content.data.strip(),
            excerpt=form.excerpt.data.strip() if form.excerpt.data else None
        )
        # Ensure slug is set and unique
        if not article.slug:
            from app.utils.ids import generate_slug
            base_slug = generate_slug(article.title)
            article.slug = article._make_unique_slug(base_slug)
        article.set_content_html()
        
        if form.is_published.data:
            article.publish()
        
        db.session.add(article)
        db.session.commit()
        
        flash('Article created successfully!', 'success')
        return redirect(url_for('articles.view', workspace_slug=workspace_slug, article_slug=article.slug))
    
    return render_template('article/create.html', workspace=workspace, form=form)


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
    
    # Check if user can view:
    # - Published articles: all workspace members can view (no restrictions)
    # - Draft articles: only author or workspace managers can view
    if article.is_published:
        # Published articles are viewable by all workspace members - no restrictions
        pass
    else:
        # Draft articles: only author or workspace managers can view
        if article.author_id != current_user.id and not can_manage_workspace(current_user, workspace):
            flash('This article is not published yet. Only the author can view it.', 'error')
            return redirect(url_for('articles.list', workspace_slug=workspace_slug))
    
    # Ensure content_html is generated if missing
    if not article.content_html and article.content:
        article.set_content_html()
        # If content_html is still empty after generation, something went wrong
        # Regenerate with a simpler approach
        if not article.content_html or not article.content_html.strip():
            # Fallback: just wrap content in paragraph tags
            import bleach
            article.content_html = bleach.clean(
                f'<p>{article.content}</p>',
                tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
                strip=False
            )
        db.session.commit()
    
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
    
    form = ArticleForm(obj=article)
    
    if form.validate_on_submit():
        article.title = form.title.data.strip()
        article.content = form.content.data.strip()
        article.excerpt = form.excerpt.data.strip() if form.excerpt.data else None
        article.set_content_html()
        article.updated_at = datetime.utcnow()
        
        if form.is_published.data and not article.is_published:
            article.publish()
        elif not form.is_published.data:
            article.is_published = False
        
        db.session.commit()
        
        flash('Article updated successfully!', 'success')
        return redirect(url_for('articles.view', workspace_slug=workspace_slug, article_slug=article.slug))
    
    return render_template('article/edit.html', workspace=workspace, article=article, form=form)


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

