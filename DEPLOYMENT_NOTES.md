# Deployment Notes

## SocketIO "Session is disconnected" Error

**Status:** ✅ Expected behavior, does not affect functionality

When using Flask-SocketIO with eventlet workers, you may see this error in logs:

```
KeyError: 'Session is disconnected'
```

### What it means:
- This occurs when a client disconnects while a request is still in progress
- It's a timing issue during SocketIO's polling transport handshake
- Flask-SocketIO handles this gracefully internally

### Impact:
- ✅ **No impact on functionality** - the app continues to work normally
- ✅ Chat, calls, and real-time features work correctly
- ⚠️ These errors appear in logs but are harmless

### Why it happens:
1. Client connects via polling transport
2. Client disconnects (browser navigation, network issue, etc.)
3. Server still tries to process a request for the disconnected session
4. Error is logged but handled gracefully

### Solutions:
1. **No action needed** - This is expected behavior with eventlet workers
2. **Upgrade to WebSocket** - Clients automatically upgrade from polling to WebSocket, which reduces these errors
3. **Configure timeouts** - Already configured with reasonable defaults

### Configuration:
The app is configured with:
- `ping_timeout=60` - Connection timeout
- `ping_interval=25` - Keepalive ping interval
- `async_mode='eventlet'` - Compatible with gunicorn eventlet workers

These settings help reduce timing issues while maintaining compatibility with production deployments.

## Other Deployment Notes

- Python 3.11.9 is required (set `PYTHON_VERSION=3.11.9` in Render)
- Eventlet worker is required for SocketIO (`--worker-class eventlet`)
- PostgreSQL is recommended for production (SQLite works but has limitations)
- SECRET_KEY must be set as an environment variable




