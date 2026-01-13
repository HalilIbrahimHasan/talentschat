# Check Database Status & Initialize

Since admin is not accessible, let's check what's happening with the database.

## Step 1: Check Database Status

Visit this URL in your browser:
```
https://talentschat-1.onrender.com/admin/setup/status
```

This will show you:
- ✅ If database is connected
- ✅ If DATABASE_URL is set
- ✅ If tables exist
- ✅ If admin user exists
- ✅ Total number of users

**Copy the JSON response and share it with me** - this will tell us exactly what's wrong.

## Step 2: Initialize Database

If the status shows database is connected but admin doesn't exist, visit:
```
https://talentschat-1.onrender.com/admin/setup/init
```

This will:
- Create all tables (if they don't exist)
- Create admin user: `admin@talentschat.com` / `admin123`

You should see a JSON response like:
```json
{
  "success": true,
  "message": "Database initialized successfully",
  "admin_user": "created",
  "admin_email": "admin@talentschat.com",
  "admin_password": "admin123",
  "total_users": 1,
  "admin_exists": true,
  "admin_is_admin": true
}
```

## Step 3: Try Login Again

After visiting `/admin/setup/init`:
1. Go to: `https://talentschat-1.onrender.com/auth/login`
2. Email: `admin@talentschat.com`
3. Password: `admin123`

## Troubleshooting

### If /admin/setup/status returns 404:
- The code changes haven't been deployed yet
- You need to commit and push the code changes first
- Wait for Render to deploy

### If /admin/setup/status shows "NOT SET" for DATABASE_URL:
- DATABASE_URL environment variable is not set in Render
- Go to Render Dashboard → Environment tab → Add DATABASE_URL
- Wait for service to restart

### If status shows connection error:
- Check the error message
- Verify DATABASE_URL is correct
- Check if PostgreSQL database is running on Render

### If admin_exists is false after running /init:
- Check the error message in the JSON response
- The traceback will show what went wrong
- Share the error with me

---

**First, visit `/admin/setup/status` and share the JSON response!**

