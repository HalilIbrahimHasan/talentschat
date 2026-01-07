from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.blueprints.workspaces import bp
from app.models.workspace import Workspace, WorkspaceMember
from app.models.channel import Channel, ChannelMember
from app.extensions import db
from app.services.permissions import can_view_workspace, can_manage_workspace


@bp.route('/')
@login_required
def dashboard():
    """List all workspaces user is member of and public workspaces"""
    memberships = WorkspaceMember.query.filter_by(user_id=current_user.id).all()
    my_workspaces = [m.workspace for m in memberships]
    my_workspace_ids = [w.id for w in my_workspaces]
    
    # Get public workspaces user is not a member of
    public_workspaces = Workspace.query.filter(
        Workspace.is_public == True,
        ~Workspace.id.in_(my_workspace_ids) if my_workspace_ids else True
    ).order_by(Workspace.created_at.desc()).limit(20).all()
    
    return render_template('workspace/dashboard.html', 
                         workspaces=my_workspaces, 
                         public_workspaces=public_workspaces)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new workspace"""
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Workspace name is required', 'error')
            return render_template('workspace/create.html')
        
        workspace = Workspace(name=name, owner_id=current_user.id, is_public=True)
        db.session.add(workspace)
        db.session.flush()
        
        # Ensure invite code is generated
        if not workspace.invite_code:
            from app.utils.ids import generate_invite_code
            workspace.invite_code = generate_invite_code()
            db.session.flush()
        
        # Add creator as owner
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=current_user.id,
            role='owner'
        )
        db.session.add(member)
        
        # Create general channel
        general = Channel(
            workspace_id=workspace.id,
            name='general',
            is_private=False,
            created_by=current_user.id
        )
        db.session.add(general)
        db.session.flush()
        
        # Add creator to general channel
        general_member = ChannelMember(channel_id=general.id, user_id=current_user.id)
        db.session.add(general_member)
        
        db.session.commit()
        flash('Workspace created successfully!', 'success')
        return redirect(url_for('channels.view', workspace_slug=workspace.slug, channel_slug='general'))
    
    return render_template('workspace/create.html')


@bp.route('/<workspace_slug>')
@login_required
def view(workspace_slug):
    """Workspace overview"""
    workspace = Workspace.query.filter_by(slug=workspace_slug).first_or_404()
    
    if not can_view_workspace(current_user, workspace):
        abort(403)
    
    from app.services.permissions import can_view_channel
    
    channels = Channel.query.filter_by(workspace_id=workspace.id).all()
    # Filter channels user can access
    accessible_channels = [ch for ch in channels if can_view_channel(current_user, ch)]
    
    # Get workspace members
    memberships = WorkspaceMember.query.filter_by(workspace_id=workspace.id).all()
    members = [m.user for m in memberships]
    
    return render_template('workspace/view.html', workspace=workspace, channels=accessible_channels, members=members)


@bp.route('/<workspace_slug>/join', methods=['GET', 'POST'])
@login_required
def join(workspace_slug):
    """Join workspace via invite code or direct join for public workspaces"""
    workspace = Workspace.query.filter_by(slug=workspace_slug).first_or_404()
    
    if request.method == 'GET':
        return render_template('workspace/join.html', workspace=workspace)
    
    invite_code = request.form.get('invite_code', '')
    
    # Check if already member
    existing = WorkspaceMember.query.filter_by(
        workspace_id=workspace.id,
        user_id=current_user.id
    ).first()
    
    if existing:
        flash('You are already a member', 'info')
        return redirect(url_for('workspaces.view', workspace_slug=workspace_slug))
    
    # Validate invite code if workspace is not public
    if not workspace.is_public:
        if not invite_code or invite_code != workspace.invite_code:
            flash('Invalid invite code', 'error')
            return render_template('workspace/join.html', workspace=workspace)
    
    # Add user as member
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role='member'
    )
    db.session.add(member)
    
    # Add user to general channel if it exists
    general_channel = Channel.query.filter_by(
        workspace_id=workspace.id,
        slug='general'
    ).first()
    if general_channel:
        channel_member = ChannelMember(channel_id=general_channel.id, user_id=current_user.id)
        db.session.add(channel_member)
    
    db.session.commit()
    flash('Joined workspace successfully!', 'success')
    return redirect(url_for('workspaces.view', workspace_slug=workspace_slug))


@bp.route('/<workspace_slug>/invite')
@login_required
def invite(workspace_slug):
    """Show invite link and code for workspace"""
    workspace = Workspace.query.filter_by(slug=workspace_slug).first_or_404()
    
    if not can_view_workspace(current_user, workspace):
        abort(403)
    
    # Generate invite link
    invite_link = request.url_root.rstrip('/') + url_for('workspaces.join', workspace_slug=workspace.slug)
    
    return render_template('workspace/invite.html', workspace=workspace, invite_link=invite_link)

