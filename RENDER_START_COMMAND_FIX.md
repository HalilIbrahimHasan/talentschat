# Fix for Render.com Start Command Error

## Problem
Render is using the wrong start command: `gunicorn app:app`
But it should use: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app`

## Solution

### Option 1: Update Start Command in Render Dashboard (RECOMMENDED)

1. Go to your Render dashboard
2. Click on your web service
3. Go to **Settings** tab
4. Scroll to **Start Command**
5. Change it to:
   ```
   gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app
   ```
6. Click **Save Changes**
7. Render will automatically redeploy

### Option 2: Use Procfile (Alternative)

Render should automatically use the Procfile if it exists. Make sure:
- Procfile is in the root directory
- It's committed to your repository
- It contains: `web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app`

## Why This Error Happened

The error `Failed to find attribute 'app' in 'app'` means:
- Render tried to import `app` module and look for `app` attribute
- But your Flask app is created in `run.py`, not in `app/__init__.py`
- The correct module path is `run:app` (import from run.py, get app variable)

## After Fixing

1. The build should succeed
2. Your app will start correctly
3. WebSockets will work (thanks to eventlet worker class)
4. Your app will be accessible at your Render URL

## Verification

After deployment, check the logs. You should see:
- Gunicorn starting with eventlet worker
- Flask app initializing
- Server listening on the correct port
- No import errors




