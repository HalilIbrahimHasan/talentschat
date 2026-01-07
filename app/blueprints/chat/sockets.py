from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio, db
from app.models.channel import Channel
from app.models.message import Message, MessageReaction, MessageHighlight
from app.services.permissions import can_view_channel
from datetime import datetime


@socketio.on('connect')
def on_connect():
    """Handle client connection"""
    if not current_user.is_authenticated:
        return False
    emit('connected', {'user_id': current_user.id, 'name': current_user.name})


@socketio.on('disconnect')
def on_disconnect():
    """Handle client disconnection"""
    pass


@socketio.on('join_room')
def on_join_room(data):
    """Join workspace+channel room"""
    if not current_user.is_authenticated:
        print(f"❌ User not authenticated for join_room")
        return False
    
    channel_id = data.get('channel_id')
    if not channel_id:
        print(f"❌ No channel_id in join_room")
        return False
    
    channel = Channel.query.get(channel_id)
    if not channel:
        print(f"❌ Channel {channel_id} not found")
        return False
    
    if not can_view_channel(current_user, channel):
        print(f"❌ User {current_user.id} cannot view channel {channel_id}")
        return False
    
    room = f'ws:{channel.workspace_id}:ch:{channel_id}'
    join_room(room)
    print(f"✅ User {current_user.id} joined room {room}")
    emit('joined_room', {'room': room, 'channel_id': channel_id})
    return True


@socketio.on('leave_room')
def on_leave_room(data):
    """Leave workspace+channel room"""
    channel_id = data.get('channel_id')
    if channel_id:
        channel = Channel.query.get(channel_id)
        if channel:
            room = f'ws:{channel.workspace_id}:ch:{channel_id}'
            leave_room(room)
            emit('left_room', {'room': room})


@socketio.on('send_message')
def on_send_message(data):
    """Handle new message"""
    if not current_user.is_authenticated:
        return False
    
    channel_id = data.get('channel_id')
    content = data.get('content', '').strip()
    reply_to_id = data.get('reply_to_id')
    video_id = data.get('video_id')  # For uploaded recordings
    
    if not channel_id or not content:
        return False
    
    channel = Channel.query.get(channel_id)
    if not channel or not can_view_channel(current_user, channel):
        return False
    
    # Check for social media video links
    from app.utils.video_embed import detect_video_url
    video_info = detect_video_url(content)
    
    # Create message
    message = Message(
        channel_id=channel_id,
        user_id=current_user.id,
        content=content,
        reply_to_id=reply_to_id
    )
    message.set_content_html()
    db.session.add(message)
    db.session.flush()  # Get message ID
    
    # Create video record if link detected or video_id provided
    if video_id:
        # Link message to uploaded video
        video = Video.query.get(video_id)
        if video:
            video.channel_id = channel_id
            db.session.commit()
    elif video_info:
        # Create external video record
        from app.models.video import Video
        video = Video(
            workspace_id=channel.workspace_id,
            channel_id=channel_id,
            uploader_id=current_user.id,
            title=f"Shared {video_info['type']} video",
            external_url=video_info['url'],
            video_type='external',
            storage_key=None
        )
        db.session.add(video)
        db.session.commit()
    
    db.session.commit()
    
    # Emit to room
    room = f'ws:{channel.workspace_id}:ch:{channel_id}'
    # Format created_at with timezone info (UTC)
    created_at_iso = message.created_at.isoformat()
    if not created_at_iso.endswith('Z') and '+' not in created_at_iso:
        created_at_iso += 'Z'  # Add Z to indicate UTC
    
    emit('message_created', {
        'id': message.id,
        'channel_id': message.channel_id,
        'user_id': message.user_id,
        'user_name': current_user.name,
        'content': message.content,
        'content_html': message.content_html,
        'created_at': created_at_iso,
        'reply_to_id': message.reply_to_id,
        'reactions': []
    }, room=room, include_self=True)


@socketio.on('add_reaction')
def on_add_reaction(data):
    """Add or remove reaction"""
    if not current_user.is_authenticated:
        print(f"❌ User not authenticated for reaction")
        return False
    
    message_id = data.get('message_id')
    emoji = data.get('emoji')
    
    print(f"📥 Received add_reaction: message_id={message_id}, emoji={emoji}, user={current_user.id}")
    
    if not message_id or not emoji:
        print(f"❌ Missing message_id or emoji")
        return False
    
    message = Message.query.get(message_id)
    if not message:
        print(f"❌ Message {message_id} not found")
        return False
    
    # Check if reaction exists
    reaction = MessageReaction.query.filter_by(
        message_id=message_id,
        user_id=current_user.id,
        emoji=emoji
    ).first()
    
    if reaction:
        # Remove reaction
        db.session.delete(reaction)
        action = 'removed'
        print(f"🗑️ Removed reaction {emoji} from message {message_id}")
    else:
        # Add reaction
        reaction = MessageReaction(
            message_id=message_id,
            user_id=current_user.id,
            emoji=emoji
        )
        db.session.add(reaction)
        action = 'added'
        print(f"➕ Added reaction {emoji} to message {message_id}")
    
    db.session.commit()
    
    # Get updated reaction counts
    from app.models.message import MessageReaction
    all_reactions = MessageReaction.query.filter_by(message_id=message_id).all()
    print(f"📊 Total reactions for message {message_id}: {len(all_reactions)}")
    for r in all_reactions:
        print(f"   - {r.emoji} by user {r.user_id}")
    
    # Emit update
    room = f'ws:{message.channel.workspace_id}:ch:{message.channel_id}'
    reaction_data = {
        'message_id': message_id,
        'emoji': emoji,
        'user_id': current_user.id,
        'action': action,
        'reactions': [{'emoji': r.emoji, 'user_id': r.user_id, 'message_id': message_id} for r in all_reactions]
    }
    print(f"📤 Emitting reaction_updated to room {room} with {len(all_reactions)} reactions")
    emit('reaction_updated', reaction_data, room=room, include_self=True)
    return True


@socketio.on('toggle_highlight')
def on_toggle_highlight(data):
    """Toggle message highlight"""
    if not current_user.is_authenticated:
        return False
    
    message_id = data.get('message_id')
    if not message_id:
        return False
    
    message = Message.query.get(message_id)
    if not message:
        return False
    
    # Check if highlighted
    highlight = MessageHighlight.query.filter_by(
        message_id=message_id,
        highlighted_by=current_user.id
    ).first()
    
    if highlight:
        # Remove highlight
        db.session.delete(highlight)
        action = 'removed'
    else:
        # Add highlight
        highlight = MessageHighlight(
            message_id=message_id,
            highlighted_by=current_user.id
        )
        db.session.add(highlight)
        action = 'added'
    
    db.session.commit()
    
    # Emit update
    room = f'ws:{message.channel.workspace_id}:ch:{message.channel_id}'
    emit('highlight_updated', {
        'message_id': message_id,
        'user_id': current_user.id,
        'action': action
    }, room=room)


@socketio.on('typing')
def on_typing(data):
    """Handle typing indicator"""
    if not current_user.is_authenticated:
        return False
    
    channel_id = data.get('channel_id')
    if not channel_id:
        return False
    
    channel = Channel.query.get(channel_id)
    if not channel or not can_view_channel(current_user, channel):
        return False
    
    room = f'ws:{channel.workspace_id}:ch:{channel_id}'
    emit('user_typing', {
        'user_id': current_user.id,
        'user_name': current_user.name,
        'channel_id': channel_id
    }, room=room, include_self=False)

