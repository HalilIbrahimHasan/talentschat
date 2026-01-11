# Fix Python 3.13 / eventlet Compatibility Issue

## Problem
Python 3.13 removed `ssl.wrap_socket` which eventlet needs. Eventlet doesn't fully support Python 3.13 yet.

## Solution: Use Python 3.11

You MUST set Python 3.11 in Render to avoid these compatibility issues.

### Steps in Render Dashboard:

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click on your web service** (talentschat)
3. **Go to Settings tab**
4. **Scroll to Environment section**
5. **Add Environment Variable:**
   - **Key**: `PYTHON_VERSION`
   - **Value**: `3.11.9`
6. **Click "Save Changes"**
7. **Render will automatically rebuild with Python 3.11**

### Alternative: Update runtime.txt (Less Reliable)

The `runtime.txt` file should have `python-3.11.9`, but Render might not always respect it. Setting the environment variable is more reliable.

## Why Python 3.11?

- ✅ Fully compatible with eventlet
- ✅ Has all the SSL/SSL features eventlet needs
- ✅ Better package ecosystem support
- ✅ Stable and well-tested
- ✅ Works perfectly with Flask-SocketIO

## After Setting PYTHON_VERSION=3.11.9

1. Render will rebuild with Python 3.11.9
2. All packages will install correctly
3. Eventlet will work without errors
4. Your app will start successfully

## Verify It Worked

After redeploy, check the logs. You should see:
- "Installing Python version 3.11.9..." (instead of 3.13.4)
- Successful package installation
- "Build successful 🎉"
- Gunicorn starting with eventlet worker
- No SSL or distutils errors


