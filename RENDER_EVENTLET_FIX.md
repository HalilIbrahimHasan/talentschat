# Fix for RuntimeError: cannot notify on un-acquired lock

## Problem

When using SQLAlchemy with `eventlet` (required for Flask-SocketIO), you may encounter:
```
RuntimeError: cannot notify on un-acquired lock
```

This happens because `eventlet` monkey-patches threading, which can conflict with SQLAlchemy's connection pool.

## Solution

Configure SQLAlchemy engine options to work with eventlet:

1. **For SQLite**: Use `NullPool` (no connection pooling) to avoid threading issues
2. **For PostgreSQL**: Use `pool_pre_ping` and `pool_recycle` for connection health

## What Was Changed

1. **`app/__init__.py`**: Added code to set `SQLALCHEMY_ENGINE_OPTIONS` dynamically based on database type
2. **`app/config.py`**: Removed static `SQLALCHEMY_ENGINE_OPTIONS` (now set dynamically)

Flask-SQLAlchemy 3.x automatically uses `SQLALCHEMY_ENGINE_OPTIONS` from the Flask config.

## Configuration Details

### SQLite (Development)
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'poolclass': NullPool,  # No pooling to avoid threading issues
    'connect_args': {'check_same_thread': False}
}
```

### PostgreSQL (Production)
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,   # Test connections before using
    'pool_recycle': 3600,    # Recycle connections after 1 hour
}
```

## Testing

After deploying, test:
1. User registration
2. User login
3. Database operations

The error should no longer occur.

