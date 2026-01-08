from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio, db
from app.models.channel import Channel
from app.models.message import Message, MessageReaction, MessageHighlight
from app.services.permissions import can_view_channel
from datetime import datetime
from collections import defaultdict

# Track online users per workspace/channel
# Structure: {room: {user_id: {'name': str, 'socket_id': str}}}
online_users = defaultdict(dict)


@socketio.on('connect')
def on_connect():
    """Handle client connection"""
    if not current_user.is_authenticated:
        return False
    print(f"✅ User {current_user.id} ({current_user.name}) connected, socket ID: {request.sid}")
    emit('connected', {'user_id': current_user.id, 'name': current_user.name})


@socketio.on('disconnect')
def on_disconnect():
    """Handle client disconnection"""
    if not current_user.is_authenticated:
        return
    
    print(f"❌ User {current_user.id} ({current_user.name}) disconnected, socket ID: {request.sid}")
    
    # Remove user from all rooms they were in
    rooms_to_update = []
    for room, users in online_users.items():
        if current_user.id in users and users[current_user.id].get('socket_id') == request.sid:
            del users[current_user.id]
            rooms_to_update.append(room)
    
    # Emit presence updates for affected rooms
    for room in rooms_to_update:
        channel_id = room.split(':')[-1] if ':' in room else None
        if channel_id:
            emit('presence_updated', {
                'channel_id': int(channel_id),
                'online_users': [{'id': uid, 'name': info['name']} for uid, info in online_users[room].items()],
                'user_id': current_user.id,
                'user_name': current_user.name,
                'status': 'offline'
            }, room=room)


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
    
    # Add user to online users for this room
    online_users[room][current_user.id] = {
        'name': current_user.name,
        'socket_id': request.sid
    }
    
    print(f"✅ User {current_user.id} joined room {room}")
    
    # Get all online users in this room
    online_users_list = [{'id': uid, 'name': info['name']} for uid, info in online_users[room].items()]
    
    # Emit joined_room with online users
    emit('joined_room', {
        'room': room, 
        'channel_id': channel_id,
        'online_users': online_users_list
    })
    
    # Notify others in the room about new user
    emit('presence_updated', {
        'channel_id': channel_id,
        'online_users': online_users_list,
        'user_id': current_user.id,
        'user_name': current_user.name,
        'status': 'online'
    }, room=room, include_self=False)
    
    return True


@socketio.on('leave_room')
def on_leave_room(data):
    """Leave workspace+channel room"""
    if not current_user.is_authenticated:
        return
    
    channel_id = data.get('channel_id')
    if channel_id:
        channel = Channel.query.get(channel_id)
        if channel:
            room = f'ws:{channel.workspace_id}:ch:{channel_id}'
            leave_room(room)
            
            # Remove user from online users
            if current_user.id in online_users[room]:
                del online_users[room][current_user.id]
            
            # Get updated online users list
            online_users_list = [{'id': uid, 'name': info['name']} for uid, info in online_users[room].items()]
            
            emit('left_room', {'room': room})
            
            # Notify others in the room
            emit('presence_updated', {
                'channel_id': channel_id,
                'online_users': online_users_list,
                'user_id': current_user.id,
                'user_name': current_user.name,
                'status': 'offline'
            }, room=room, include_self=False)


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


# Call signaling - track active calls
# {call_id: {'participants': [user_ids], 'type': 'video'|'audio', 'creator_id': int}}
active_calls = {}


@socketio.on('initiate_call')
def on_initiate_call(data):
    """Initiate a call"""
    if not current_user.is_authenticated:
        return False
    
    callee_id = data.get('callee_id')
    call_type = data.get('type', 'video')  # 'video' or 'audio'
    
    if not callee_id:
        return False
    
    # Get callee's socket ID from online users
    callee_socket_id = None
    caller_room = None
    for room, users in online_users.items():
        if callee_id in users:
            callee_socket_id = users[callee_id].get('socket_id')
        if current_user.id in users:
            caller_room = room
        if callee_socket_id and caller_room:
            break
    
    if not callee_socket_id:
        emit('call_error', {'message': 'User is not online'})
        return False
    
    call_id = f"call_{current_user.id}_{callee_id}_{int(datetime.utcnow().timestamp())}"
    active_calls[call_id] = {
        'participants': [current_user.id, callee_id],
        'type': call_type,
        'creator_id': current_user.id,
        'room': caller_room
    }
    
    # Emit to callee
    emit('incoming_call', {
        'call_id': call_id,
        'caller_id': current_user.id,
        'caller_name': current_user.name,
        'type': call_type,
        'participants': [{'id': current_user.id, 'name': current_user.name}]
    }, room=callee_socket_id)
    
    return {'call_id': call_id}


@socketio.on('accept_call')
def on_accept_call(data):
    """Accept a call"""
    if not current_user.is_authenticated:
        return False
    
    call_id = data.get('call_id')
    if not call_id or call_id not in active_calls:
        return False
    
    call = active_calls[call_id]
    if current_user.id not in call['participants']:
        call['participants'].append(current_user.id)
    
    # Notify all other participants
    participants_to_notify = [uid for uid in call['participants'] if uid != current_user.id]
    for participant_id in participants_to_notify:
        participant_socket_id = None
        for room, users in online_users.items():
            if participant_id in users:
                participant_socket_id = users[participant_id].get('socket_id')
                break
        
        if participant_socket_id:
            emit('call_accepted', {
                'call_id': call_id,
                'callee_id': current_user.id,
                'callee_name': current_user.name
            }, room=participant_socket_id)
    
    # Notify about participant joined to all
    for participant_id in call['participants']:
        if participant_id != current_user.id:
            participant_socket_id = None
            for room, users in online_users.items():
                if participant_id in users:
                    participant_socket_id = users[participant_id].get('socket_id')
                    break
            
            if participant_socket_id:
                emit('participant_joined', {
                    'call_id': call_id,
                    'user_id': current_user.id,
                    'user_name': current_user.name
                }, room=participant_socket_id)
    
    return True


@socketio.on('reject_call')
def on_reject_call(data):
    """Reject a call"""
    if not current_user.is_authenticated:
        return False
    
    call_id = data.get('call_id')
    if not call_id or call_id not in active_calls:
        return False
    
    call = active_calls[call_id]
    
    # Notify all participants
    for participant_id in call['participants']:
        if participant_id != current_user.id:
            participant_socket_id = None
            for room, users in online_users.items():
                if participant_id in users:
                    participant_socket_id = users[participant_id].get('socket_id')
                    break
            
            if participant_socket_id:
                emit('call_rejected', {
                    'call_id': call_id,
                    'callee_id': current_user.id
                }, room=participant_socket_id)
    
    # Remove call if only creator remains or remove user from participants
    if len(call['participants']) <= 1 or call['creator_id'] == current_user.id:
        if call_id in active_calls:
            del active_calls[call_id]
    else:
        call['participants'].remove(current_user.id)
    
    return True


@socketio.on('end_call')
def on_end_call(data):
    """End a call"""
    if not current_user.is_authenticated:
        return False
    
    call_id = data.get('call_id')
    if not call_id or call_id not in active_calls:
        return False
    
    call = active_calls[call_id]
    
    # Notify all participants
    for participant_id in call['participants']:
        if participant_id != current_user.id:
            participant_socket_id = None
            for room, users in online_users.items():
                if participant_id in users:
                    participant_socket_id = users[participant_id].get('socket_id')
                    break
            
            if participant_socket_id:
                emit('call_ended', {
                    'call_id': call_id,
                    'ended_by': current_user.id
                }, room=participant_socket_id)
                emit('participant_left', {
                    'call_id': call_id,
                    'user_id': current_user.id
                }, room=participant_socket_id)
    
    # Remove call
    if call_id in active_calls:
        del active_calls[call_id]
    
    return True


@socketio.on('call_ice_candidate')
def on_call_ice_candidate(data):
    """Handle ICE candidate for WebRTC"""
    if not current_user.is_authenticated:
        return False
    
    call_id = data.get('call_id')
    candidate = data.get('candidate')
    to_user_id = data.get('to_user_id')
    
    if not call_id or call_id not in active_calls:
        return False
    
    call = active_calls[call_id]
    if current_user.id not in call['participants']:
        return False
    
    # Forward ICE candidate to target user
    target_socket_id = None
    for room, users in online_users.items():
        if to_user_id in users:
            target_socket_id = users[to_user_id].get('socket_id')
            break
    
    if target_socket_id:
        emit('call_ice_candidate', {
            'call_id': call_id,
            'candidate': candidate,
            'from_user_id': current_user.id
        }, room=target_socket_id)
    
    return True


@socketio.on('add_participant')
def on_add_participant(data):
    """Add participant to existing call"""
    if not current_user.is_authenticated:
        return False
    
    call_id = data.get('call_id')
    user_id = data.get('user_id')
    
    if not call_id or call_id not in active_calls:
        return False
    
    call = active_calls[call_id]
    if current_user.id not in call['participants']:
        return False
    
    if user_id not in call['participants']:
        call['participants'].append(user_id)
        
        # Get user's socket ID
        user_socket_id = None
        for room, users in online_users.items():
            if user_id in users:
                user_socket_id = users[user_id].get('socket_id')
                break
        
        if user_socket_id:
            # Notify user about incoming call
            emit('incoming_call', {
                'call_id': call_id,
                'caller_id': current_user.id,
                'caller_name': current_user.name,
                'type': call['type'],
                'participants': [{'id': uid, 'name': 'User'} for uid in call['participants'] if uid != user_id]
            }, room=user_socket_id)
            
            # Get user name
            from app.models.user import User
            user = User.query.get(user_id)
            user_name = user.name if user else 'User'
            
            # Notify existing participants
            for participant_id in call['participants']:
                if participant_id != user_id and participant_id != current_user.id:
                    participant_socket_id = None
                    for room, users in online_users.items():
                        if participant_id in users:
                            participant_socket_id = users[participant_id].get('socket_id')
                            break
                    
                    if participant_socket_id:
                        emit('participant_joined', {
                            'call_id': call_id,
                            'user_id': user_id,
                            'user_name': user_name
                        }, room=participant_socket_id)
    
    return True


@socketio.on('call_offer')
def on_call_offer(data):
    """Handle WebRTC offer"""
    if not current_user.is_authenticated:
        return False
    
    call_id = data.get('call_id')
    offer = data.get('offer')
    to_user_id = data.get('to_user_id')
    
    if not call_id or call_id not in active_calls:
        return False
    
    call = active_calls[call_id]
    if current_user.id not in call['participants']:
        return False
    
    # Forward offer to target user
    target_socket_id = None
    for room, users in online_users.items():
        if to_user_id in users:
            target_socket_id = users[to_user_id].get('socket_id')
            break
    
    if target_socket_id:
        emit('call_offer', {
            'call_id': call_id,
            'offer': offer,
            'from_user_id': current_user.id
        }, room=target_socket_id)
    
    return True


@socketio.on('call_answer')
def on_call_answer(data):
    """Handle WebRTC answer"""
    if not current_user.is_authenticated:
        return False
    
    call_id = data.get('call_id')
    answer = data.get('answer')
    to_user_id = data.get('to_user_id')
    
    if not call_id or call_id not in active_calls:
        return False
    
    call = active_calls[call_id]
    if current_user.id not in call['participants']:
        return False
    
    # Forward answer to target user
    target_socket_id = None
    for room, users in online_users.items():
        if to_user_id in users:
            target_socket_id = users[to_user_id].get('socket_id')
            break
    
    if target_socket_id:
        emit('call_answer', {
            'call_id': call_id,
            'answer': answer,
            'from_user_id': current_user.id
        }, room=target_socket_id)
    
    return True

