from app.models.workspace import WorkspaceMember
from app.models.channel import ChannelMember


def can_view_workspace(user, workspace):
    """Check if user can view workspace"""
    if not user or not workspace:
        return False
    return WorkspaceMember.query.filter_by(
        workspace_id=workspace.id,
        user_id=user.id
    ).first() is not None


def can_manage_workspace(user, workspace):
    """Check if user can manage workspace (owner/admin)"""
    if not user or not workspace:
        return False
    member = WorkspaceMember.query.filter_by(
        workspace_id=workspace.id,
        user_id=user.id
    ).first()
    return member and member.role in ('owner', 'admin')


def can_view_channel(user, channel):
    """Check if user can view channel"""
    if not user or not channel:
        return False
    
    # Check workspace membership
    if not can_view_workspace(user, channel.workspace):
        return False
    
    # Public channels are viewable by all workspace members
    if not channel.is_private:
        return True
    
    # Private channels require explicit membership
    return ChannelMember.query.filter_by(
        channel_id=channel.id,
        user_id=user.id
    ).first() is not None


def can_manage_channel(user, channel):
    """Check if user can manage channel"""
    if not user or not channel:
        return False
    
    # Workspace admins/owners can manage
    if can_manage_workspace(user, channel.workspace):
        return True
    
    # Channel creator can manage
    return channel.created_by == user.id




