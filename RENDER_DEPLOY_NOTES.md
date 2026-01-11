# Render.com Deployment Notes

## Fixed Issues

### Pillow Installation Error
- **Problem**: Pillow 10.1.0 doesn't build on Python 3.13
- **Solution**: Updated to Pillow>=10.3.0 which supports Python 3.13
- **Alternative**: Use Python 3.11.9 (set in runtime.txt) which has better package support

## Deployment Steps for Render.com

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure Settings:**
   ```
   Name: talentschat (or your choice)
   Environment: Python 3
   Branch: main (or your default branch)
   Root Directory: . (leave empty)
   ```

4. **Build & Start Commands:**
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app
   ```

5. **Environment Variables:**
   - `SECRET_KEY`: Generate with `python3 -c "import secrets; print(secrets.token_hex(32))"`
   - `FLASK_ENV`: `production`
   - `DATABASE_URL`: (will be set automatically if you add PostgreSQL database)

6. **Add PostgreSQL Database (Recommended for Production):**
   - In Render dashboard, click "New +" → "PostgreSQL"
   - Choose free tier
   - Copy the "Internal Database URL"
   - Add as environment variable `DATABASE_URL` in your web service

7. **Deploy!**
   - Click "Create Web Service"
   - Wait 3-5 minutes for first deployment

## Troubleshooting

### If Build Still Fails:

1. **Check Python Version**: Render should use Python 3.11.9 (from runtime.txt)
2. **Check Build Logs**: Look for specific package errors
3. **Try Python 3.11 explicitly**: Set in runtime.txt (already done)

### Common Issues:

- **Pillow errors**: Should be fixed with updated version
- **Database connection errors**: Make sure DATABASE_URL is set correctly
- **Port errors**: Use $PORT environment variable (already in start command)
- **Static files**: Should work automatically with Flask

## After Deployment

1. Your app will be available at: `https://your-app-name.onrender.com`
2. First visit may take 30-60 seconds (cold start on free tier)
3. Create your first user account
4. Start using TalentsChat!

## Free Tier Limitations

- Services spin down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 750 hours/month free (enough for one service running 24/7)
- PostgreSQL: 90 days free, then requires paid plan

## Upgrading (Optional)

If you need:
- Always-on service (no spin-down)
- More resources
- Persistent PostgreSQL

Consider upgrading to a paid plan.


