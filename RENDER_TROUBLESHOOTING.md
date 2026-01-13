# Troubleshooting Render Deployment Errors

## How to Check Logs in Render

1. Go to https://dashboard.render.com
2. Click on your service (talentschat)
3. Click on **"Logs"** tab (in the left sidebar)
4. Look for error messages, tracebacks, or exceptions

## Common Issues After Deployment

### 1. Internal Server Error on Registration

**Possible Causes:**
- Database tables not created
- Database connection issues
- Missing SECRET_KEY
- File permission errors (uploads directory)

**Check Logs For:**
- SQLAlchemy errors
- Permission denied errors
- Import errors
- Database connection errors

### 2. Database Issues

If using SQLite (default):
- SQLite files need write permissions
- The database file might not exist yet
- Tables might not be created

If using PostgreSQL:
- Check DATABASE_URL is set correctly
- Verify database is created and accessible
- Check connection string format

### 3. Missing Environment Variables

Required variables:
- `SECRET_KEY` - Must be set!
- `FLASK_ENV=production`
- `DATABASE_URL` - If using PostgreSQL

### 4. File Upload Issues

The uploads directory needs to be writable. Check logs for permission errors.

## Quick Fixes

1. **Check Render Logs** - Most errors will show in the logs
2. **Verify Environment Variables** - Make sure SECRET_KEY is set
3. **Check Database** - Tables should auto-create on first request
4. **Review Error Message** - Copy the full error from logs




