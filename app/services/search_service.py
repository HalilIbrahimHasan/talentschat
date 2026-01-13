# Placeholder for future search functionality
# For MVP, we'll use simple SQL LIKE queries
# In v1.1, implement full-text search (FTS)

def search_messages(query, channel_id=None, limit=50):
    """Search messages (simple LIKE for MVP)"""
    from app.models.message import Message
    from app.extensions import db
    
    q = Message.query.filter(Message.content.contains(query))
    if channel_id:
        q = q.filter_by(channel_id=channel_id)
    return q.order_by(Message.created_at.desc()).limit(limit).all()




