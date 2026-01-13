# Fix for Render.com Build Command Error

## Problem
Render is using the START command as the BUILD command. The error shows:
```
==> Running build command 'gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app'...
bash: line 1: gunicorn: command not found
```

This means:
- Build Command is set to the start command (WRONG)
- Start Command might also be wrong
- Gunicorn isn't installed yet because dependencies aren't being installed

## Solution

### Update Settings in Render Dashboard

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click on your web service** (talentschat)
3. **Go to Settings tab**
4. **Update these two fields:**

   **Build Command** (install dependencies):
   ```
   pip install -r requirements.txt
   ```
   
   **Start Command** (run the app):
   ```
   gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app
   ```

5. **Click "Save Changes"**
6. **Render will automatically redeploy**

## Why This Happened

Render has TWO separate commands:
- **Build Command**: Runs ONCE to install dependencies and prepare your app
- **Start Command**: Runs EVERY TIME your service starts to actually run your app

These were mixed up, so Render was trying to run gunicorn before installing it.

## Step-by-Step in Render Dashboard

1. Open your service in Render
2. Click **Settings** (left sidebar)
3. Scroll to **Build & Deploy**
4. Find **Build Command** field
5. Set it to: `pip install -r requirements.txt`
6. Find **Start Command** field  
7. Set it to: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app`
8. Click **Save Changes** at the bottom
9. Wait for automatic redeploy (2-5 minutes)

## After Fixing

You should see in the logs:
1. ✅ Python version installation
2. ✅ Running build command: `pip install -r requirements.txt`
3. ✅ Installing packages (Flask, gunicorn, etc.)
4. ✅ Build successful
5. ✅ Running start command: `gunicorn --worker-class eventlet...`
6. ✅ Application starting
7. ✅ Server listening on port

## Optional: Python Version

If you want to use Python 3.11 instead of 3.13 (better compatibility), you can also set:
- **Environment Variable**: `PYTHON_VERSION=3.11.9`
- Or Render should read `runtime.txt` (but you may need to set it as env var)

But Python 3.13 should work fine now that Pillow is updated.




