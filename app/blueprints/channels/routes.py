from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.blueprints.channels import bp
from app.models.workspace import Workspace, WorkspaceMember
from app.models.channel import Channel, ChannelMember
from app.extensions import db
from app.services.permissions import can_view_workspace, can_view_channel, can_manage_channel


@bp.route('/<channel_slug>')
@login_required
def view(workspace_slug, channel_slug):
    """Channel chat view"""
    workspace = Workspace.query.filter_by(slug=workspace_slug).first_or_404()
    
    if not can_view_workspace(current_user, workspace):
        abort(403)
    
    channel = Channel.query.filter_by(
        workspace_id=workspace.id,
        slug=channel_slug
    ).first_or_404()
    
    if not can_view_channel(current_user, channel):
        abort(403)
    
    # Get all channels for sidebar - filter by accessibility
    all_channels = Channel.query.filter_by(workspace_id=workspace.id).all()
    accessible_channels = []
    for ch in all_channels:
        if can_view_channel(current_user, ch):
            accessible_channels.append(ch)
    
    # Get pinned messages
    from app.models.message import MessagePin
    pins = MessagePin.query.filter_by(channel_id=channel.id).order_by(MessagePin.created_at.desc()).limit(10).all()
    pinned_messages = [pin.message for pin in pins]
    
    # Get highlights
    from app.models.message import MessageHighlight
    highlights = MessageHighlight.query.join(MessageHighlight.message).filter(
        MessageHighlight.message.has(channel_id=channel.id)
    ).order_by(MessageHighlight.created_at.desc()).limit(10).all()
    highlighted_messages = [h.message for h in highlights]
    
    # Get workspace members for adding to calls (extract User objects from WorkspaceMember)
    memberships = WorkspaceMember.query.filter_by(workspace_id=workspace.id).all()
    members = [m.user for m in memberships]
    
    return render_template(
        'channel/view.html',
        workspace=workspace,
        channel=channel,
        channels=accessible_channels,
        pinned_messages=pinned_messages,
        highlighted_messages=highlighted_messages,
        members=members
    )


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create(workspace_slug):
    """Create new channel"""
    workspace = Workspace.query.filter_by(slug=workspace_slug).first_or_404()
    
    if not can_view_workspace(current_user, workspace):
        abort(403)
    
    if request.method == 'POST':
        name = request.form.get('name')
        is_private = request.form.get('is_private') == 'on'
        
        if not name:
            flash('Channel name is required', 'error')
            return render_template('channel/create.html', workspace=workspace)
        
        channel = Channel(
            workspace_id=workspace.id,
            name=name,
            is_private=is_private,
            created_by=current_user.id
        )
        db.session.add(channel)
        db.session.flush()
        
        # Add creator as member
        member = ChannelMember(channel_id=channel.id, user_id=current_user.id)
        db.session.add(member)
        
        db.session.commit()
        flash('Channel created successfully!', 'success')
        return redirect(url_for('channels.view', workspace_slug=workspace_slug, channel_slug=channel.slug))
    
    return render_template('channel/create.html', workspace=workspace)

