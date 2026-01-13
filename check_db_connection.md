# How to Check if Database is Connected

Based on your logs, here's what I can see:

## ✅ Good Signs:
- `psycopg2-binary` is installed (PostgreSQL driver)
- App is running without errors
- User registration worked (302 redirect)
- No database connection errors in logs

## ❓ Can't Tell From Logs:
- Whether DATABASE_URL is set (would only show error if missing/wrong)
- Whether tables exist in PostgreSQL
- Whether admin user exists
- Whether Python challenges are in database

## 🔍 How to Verify Connection:

### Option 1: Check Environment Variables in Render
1. Go to Render Dashboard → Your Service → Environment tab
2. Look for `DATABASE_URL` - is it set?
3. If not set → **Not connected to PostgreSQL** (using SQLite instead)

### Option 2: Check Render Logs for Database Messages
Look for messages like:
- "Creating tables..."
- Database connection errors
- SQLAlchemy errors

### Option 3: Test in Render Shell
1. Go to Render Service → Shell tab
2. Run:
   ```python
   python3 -c "import os; print('DATABASE_URL:', os.environ.get('DATABASE_URL', 'NOT SET'))"
   ```

### Option 4: Try to Login as Admin
- Try: `admin@talentschat.com` / `admin123`
- If login fails → Database not initialized yet
- If login works → Database is connected!

### Option 5: Check if Python Challenges Show
- Visit: `/learn/code` (coding challenges page)
- If empty → Database not initialized
- If shows challenges → Database is connected!

## Most Likely Status:

Based on your earlier message ("admin user does not exist, python questions not visible"):
- ✅ Database might be connected (no errors)
- ❌ But database is NOT initialized (no tables, no admin, no challenges)

## Next Step:

If DATABASE_URL is set but data is missing, you need to initialize:
1. Go to Render Service → Shell
2. Run: `python3 init_postgres_db.py`
3. Run: `python3 add_python_challenges.py`

This will create tables, admin user, and add challenges.

