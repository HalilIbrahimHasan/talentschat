from datetime import datetime, timedelta


def format_relative_time(dt):
    """Format datetime as relative time (e.g., '2 hours ago')"""
    if not dt:
        return ''
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return 'just now'
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f'{minutes}m ago'
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f'{hours}h ago'
    elif diff < timedelta(days=7):
        days = diff.days
        return f'{days}d ago'
    else:
        return dt.strftime('%b %d, %Y')


def format_datetime(dt):
    """Format datetime as readable string"""
    if not dt:
        return ''
    return dt.strftime('%Y-%m-%d %H:%M:%S')

