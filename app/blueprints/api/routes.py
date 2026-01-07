from flask import jsonify, request, abort
from flask_login import login_required, current_user
from datetime import datetime
from app.blueprints.api import bp
from app.models.channel import Channel
from app.models.message import Message, MessageReaction, MessageHighlight
from app.models.file import File, Snippet
from app.models.video import Video, VideoLike, VideoComment
from app.extensions import db
from app.services.permissions import can_view_channel, can_view_workspace
from app.services.upload_service import save_uploaded_file, get_file_type, allowed_file
from app.config import Config


@bp.route('/channels/<int:channel_id>/messages')
@login_required
def get_messages(channel_id):
    """Get messages for channel with pagination"""
    channel = Channel.query.get_or_404(channel_id)
    
    if not can_view_channel(current_user, channel):
        abort(403)
    
    before = request.args.get('before')
    limit = int(request.args.get('limit', 50))
    
    query = Message.query.filter_by(channel_id=channel_id)
    if before:
        try:
            before_dt = datetime.fromisoformat(before)
            query = query.filter(Message.created_at < before_dt)
        except:
            pass
    
    messages = query.order_by(Message.created_at.desc()).limit(limit).all()
    messages.reverse()  # Oldest first
    
    # Build response with reactions
    result = []
    for m in messages:
        # Get all reactions for this message
        reactions = MessageReaction.query.filter_by(message_id=m.id).all()
        reaction_data = [{'emoji': r.emoji, 'user_id': r.user_id, 'message_id': m.id} for r in reactions]
        
        # Format created_at with timezone info (UTC)
        created_at_iso = m.created_at.isoformat()
        if not created_at_iso.endswith('Z') and '+' not in created_at_iso:
            created_at_iso += 'Z'  # Add Z to indicate UTC
        
        result.append({
            'id': m.id,
            'user_id': m.user_id,
            'user_name': m.user.name,
            'content': m.content,
            'content_html': m.content_html,
            'created_at': created_at_iso,
            'reply_to_id': m.reply_to_id,
            'reactions': reaction_data,
            'highlighted': any(h.highlighted_by == current_user.id for h in m.highlights)
        })
    
    return jsonify(result)


@bp.route('/messages', methods=['POST'])
@login_required
def create_message():
    """Fallback message creation if websocket fails"""
    data = request.get_json()
    channel_id = data.get('channel_id')
    content = data.get('content', '').strip()
    
    if not channel_id or not content:
        return jsonify({'error': 'Missing channel_id or content'}), 400
    
    channel = Channel.query.get(channel_id)
    if not channel or not can_view_channel(current_user, channel):
        abort(403)
    
    message = Message(
        channel_id=channel_id,
        user_id=current_user.id,
        content=content
    )
    message.set_content_html()
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'id': message.id,
        'user_id': message.user_id,
        'user_name': current_user.name,
        'content': message.content,
        'content_html': message.content_html,
        'created_at': (message.created_at.isoformat() + 'Z') if not message.created_at.isoformat().endswith('Z') and '+' not in message.created_at.isoformat() else message.created_at.isoformat()
    }), 201


@bp.route('/messages/<int:message_id>/reactions', methods=['POST'])
@login_required
def toggle_reaction(message_id):
    """Toggle reaction on message"""
    try:
        data = request.get_json() or {}
        emoji = data.get('emoji')
        
        print(f"📥 HTTP: Received reaction request for message {message_id}, emoji={emoji}, user={current_user.id}, data={data}")
        
        if not emoji:
            print(f"❌ HTTP: Missing emoji in request")
            return jsonify({'error': 'Missing emoji'}), 400
        
        message = Message.query.get_or_404(message_id)
        
        if not can_view_channel(current_user, message.channel):
            abort(403)
        
        reaction = MessageReaction.query.filter_by(
            message_id=message_id,
            user_id=current_user.id,
            emoji=emoji
        ).first()
        
        if reaction:
            db.session.delete(reaction)
            action = 'removed'
            print(f"🗑️ HTTP: Removed reaction {emoji} from message {message_id}")
        else:
            reaction = MessageReaction(
                message_id=message_id,
                user_id=current_user.id,
                emoji=emoji
            )
            db.session.add(reaction)
            action = 'added'
            print(f"➕ HTTP: Added reaction {emoji} to message {message_id}")
        
        db.session.commit()
        
        # Get all reactions for this message
        all_reactions = MessageReaction.query.filter_by(message_id=message_id).all()
        print(f"📊 HTTP: Total reactions for message {message_id}: {len(all_reactions)}")
        
        return jsonify({
            'action': action, 
            'emoji': emoji,
            'message_id': message_id,
            'reactions': [{'emoji': r.emoji, 'user_id': r.user_id, 'message_id': message_id} for r in all_reactions]
        })
    except Exception as e:
        print(f"❌ HTTP: Error in toggle_reaction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/messages/<int:message_id>/highlight', methods=['POST'])
@login_required
def toggle_highlight(message_id):
    """Toggle highlight on message"""
    message = Message.query.get_or_404(message_id)
    
    if not can_view_channel(current_user, message.channel):
        abort(403)
    
    highlight = MessageHighlight.query.filter_by(
        message_id=message_id,
        highlighted_by=current_user.id
    ).first()
    
    if highlight:
        db.session.delete(highlight)
        action = 'removed'
    else:
        highlight = MessageHighlight(
            message_id=message_id,
            highlighted_by=current_user.id
        )
        db.session.add(highlight)
        action = 'added'
    
    db.session.commit()
    
    return jsonify({'action': action})


@bp.route('/videos/<int:video_id>/like', methods=['POST'])
@login_required
def toggle_video_like(video_id):
    """Toggle like on video"""
    video = Video.query.get_or_404(video_id)
    
    if not can_view_workspace(current_user, video.workspace):
        abort(403)
    
    like = VideoLike.query.filter_by(
        video_id=video_id,
        user_id=current_user.id
    ).first()
    
    if like:
        db.session.delete(like)
        action = 'unliked'
    else:
        like = VideoLike(
            video_id=video_id,
            user_id=current_user.id
        )
        db.session.add(like)
        action = 'liked'
    
    db.session.commit()
    
    like_count = len(video.likes)
    
    return jsonify({'action': action, 'like_count': like_count})


@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload file or video"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    file_type_param = request.form.get('type', 'documents')
    workspace_id = request.form.get('workspace_id', type=int)
    channel_id = request.form.get('channel_id', type=int)
    
    if not workspace_id:
        return jsonify({'error': 'Missing workspace_id'}), 400
    
    from app.models.workspace import Workspace
    workspace = Workspace.query.get_or_404(workspace_id)
    
    if not can_view_workspace(current_user, workspace):
        abort(403)
    
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400
    
    # Determine file type
    detected_type = get_file_type(file.filename)
    if file_type_param == 'video':
        detected_type = 'videos'
    
    # Validate file
    if not allowed_file(file.filename, detected_type):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Check size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset
    
    if detected_type == 'videos' and size > Config.MAX_VIDEO_SIZE:
        return jsonify({'error': 'Video too large'}), 400
    elif detected_type != 'videos' and size > Config.MAX_DOC_SIZE:
        return jsonify({'error': 'File too large'}), 400
    
    try:
        storage_key = save_uploaded_file(file, detected_type, str(workspace_id))
        
        if detected_type == 'videos':
            # Create video record
            video = Video(
                workspace_id=workspace_id,
                channel_id=channel_id,
                uploader_id=current_user.id,
                title=file.filename,
                storage_key=str(storage_key)
            )
            db.session.add(video)
            db.session.commit()
            
            return jsonify({
                'type': 'video',
                'id': video.id,
                'filename': file.filename,
                'storage_key': str(storage_key)
            }), 201
        else:
            # Create file record
            file_record = File(
                workspace_id=workspace_id,
                channel_id=channel_id,
                uploader_id=current_user.id,
                filename=file.filename,
                mime=file.content_type or 'application/octet-stream',
                size=size,
                storage_key=str(storage_key)
            )
            db.session.add(file_record)
            db.session.commit()
            
            return jsonify({
                'type': 'file',
                'id': file_record.id,
                'filename': file.filename,
                'storage_key': str(storage_key),
                'size': size
            }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/videos/<int:video_id>/comments', methods=['POST'])
@login_required
def add_video_comment(video_id):
    """Add comment to video"""
    video = Video.query.get_or_404(video_id)
    
    if not can_view_workspace(current_user, video.workspace):
        abort(403)
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Comment content required'}), 400
    
    comment = VideoComment(
        video_id=video_id,
        user_id=current_user.id,
        content=content
    )
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'id': comment.id,
        'user_id': comment.user_id,
        'user_name': current_user.name,
        'content': comment.content,
        'created_at': comment.created_at.isoformat()
    }), 201

