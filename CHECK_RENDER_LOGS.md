# How to Check Render Logs and Fix Errors

## Step 1: Check Render Logs

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click on your service** (talentschat-1)
3. **Click "Logs" tab** (in the left sidebar)
4. **Look for error messages** - scroll through the logs to find:
   - Tracebacks (Python errors)
   - Database errors
   - Import errors
   - Permission errors

## Common Errors and Fixes

### Error: Database Connection Issues

**If you see SQLAlchemy errors:**
- Check if `DATABASE_URL` is set
- If using PostgreSQL, verify the connection string
- If using SQLite, check file permissions

### Error: PRAGMA table_info (SQLite-specific)

**If you see:** `syntax error at or near "PRAGMA"`
- This means you're using PostgreSQL but the code is trying SQLite commands
- **Fix:** I've updated the code to only run SQLite migrations when using SQLite
- Commit and push the updated `app/__init__.py`

### Error: No such table / Table doesn't exist

**If tables aren't created:**
- The `db.create_all()` should create them
- Check if database connection is working
- Verify DATABASE_URL is correct

### Error: Permission denied / File not writable

**If you see file permission errors:**
- SQLite database file needs write permissions
- Uploads directory needs write permissions
- This is usually automatic on Render

### Error: Missing SECRET_KEY

**If you see CSRF or session errors:**
- Make sure `SECRET_KEY` environment variable is set
- Generate one if missing: `python3 -c "import secrets; print(secrets.token_hex(32))"`

## What to Look For in Logs

Copy the FULL error traceback from the logs. It will show:
- The exact error message
- Which file/line caused it
- What operation failed

## After Finding the Error

1. Copy the full error message
2. Share it here or check common fixes above
3. Most errors can be fixed by:
   - Setting environment variables
   - Fixing database connection
   - Updating code to handle production environment

## Quick Fixes to Try

1. **Check Environment Variables:**
   - SECRET_KEY is set
   - FLASK_ENV=production
   - DATABASE_URL (if using PostgreSQL)

2. **Verify Database:**
   - Tables should auto-create on first request
   - Check if database connection works

3. **Check Code:**
   - Make sure migrations only run for SQLite (fixed in latest code)
   - Verify all imports work

