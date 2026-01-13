# How to Connect Your App to PostgreSQL on Render

## Quick Steps

### Step 1: Set DATABASE_URL in Render Dashboard

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click on your web service** (the one running your Flask app)
3. **Click "Environment" tab** (in the left sidebar)
4. **Click "Add Environment Variable"** button
5. **Add this variable:**
   - **Key:** `DATABASE_URL`
   - **Value:** `postgresql://talentschatdb_user:PexPT6558fFTGuly9RSPIe92nbVEMzEu@dpg-d5ir02n5r7bs73dk7cv0-a.oregon-postgres.render.com:5432/talentschatdb`
6. **Click "Save Changes"**

### Step 2: Initialize Database Using Render Shell

1. **In your Render service**, click **"Shell" tab** (in the left sidebar)
2. **Wait for the shell to connect** (may take 10-20 seconds)
3. **Run these commands one by one:**

```bash
export DATABASE_URL="postgresql://talentschatdb_user:PexPT6558fFTGuly9RSPIe92nbVEMzEu@dpg-d5ir02n5r7bs73dk7cv0-a.oregon-postgres.render.com:5432/talentschatdb"
```

```bash
python3 init_postgres_db.py
```

```bash
python3 add_python_challenges.py
```

### Step 3: Restart Your Service

1. **Go back to your service** (click service name in breadcrumb)
2. **Click "Manual Deploy"** → **"Clear build cache & deploy"** (or just restart the service)
3. **Wait for deployment to complete**

### Step 4: Verify Connection

1. **Check Logs** - Click "Logs" tab, you should see:
   - No database connection errors
   - Tables created successfully
   
2. **Try to login:**
   - Go to your app URL
   - Login page: `/auth/login`
   - Email: `admin@talentschat.com`
   - Password: `admin123`

3. **Check Python challenges:**
   - Go to: `/learn/coding-challenges`
   - Should see 100+ Python challenges

## What Each Step Does

- **Step 1**: Tells your app to use PostgreSQL instead of SQLite
- **Step 2**: Creates tables and adds admin user + Python challenges
- **Step 3**: Restarts app so it uses the new DATABASE_URL
- **Step 4**: Confirms everything is working

## Troubleshooting

### If Shell doesn't work:
- Make sure your service is running
- Try refreshing the page
- Wait a bit longer for shell to connect

### If initialization fails:
- Check that DATABASE_URL is correct in Environment tab
- Copy the exact connection string (no extra spaces)
- Check Render logs for error messages

### If app still uses SQLite:
- Make sure DATABASE_URL is saved in Environment tab
- Restart the service after adding DATABASE_URL
- Check logs to see which database it's connecting to

## Important Notes

- ✅ `psycopg2-binary` is already in `requirements.txt` - Render will install it automatically
- ✅ The app will automatically use PostgreSQL when DATABASE_URL is set
- ✅ Tables will be created automatically when app starts (but running scripts ensures admin user is created)
- ⚠️ You only need to run the scripts once to initialize the database

## Current Status Checklist

- [ ] DATABASE_URL environment variable set in Render
- [ ] Database initialized (tables created)
- [ ] Admin user created
- [ ] Python challenges added
- [ ] Service restarted
- [ ] Can login as admin
- [ ] Can see Python challenges

Follow these steps in order and your app will be connected to PostgreSQL! 🚀

