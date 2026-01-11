# Deployment Guide for TalentsChat

This Flask application can be deployed to various platforms. Netlify is **not suitable** for Flask applications as it's designed for static sites. Use one of the platforms below instead.

## Recommended Platforms

### 1. Render.com (Recommended - Free Tier Available)

1. **Create a Render account** at https://render.com
2. **Create a new Web Service**
3. **Connect your repository** (GitHub/GitLab/Bitbucket)
4. **Configure the service:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app`
   - **Environment**: Python 3
5. **Add Environment Variables:**
   - `SECRET_KEY`: Generate a secure random key (you can use: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `DATABASE_URL`: For PostgreSQL (Render provides free PostgreSQL)
   - `FLASK_ENV=production`
6. **Deploy**

**Note**: For PostgreSQL, you'll need to:
- Create a PostgreSQL database in Render
- Use the connection string as `DATABASE_URL`
- Install `psycopg2-binary` in requirements.txt for PostgreSQL support

### 2. Railway.app (Easy Setup)

1. **Create a Railway account** at https://railway.app
2. **Create a new project** and connect your repository
3. **Railway will auto-detect** it's a Python app
4. **Add Environment Variables:**
   - `SECRET_KEY`
   - `DATABASE_URL` (Railway provides PostgreSQL)
   - `FLASK_ENV=production`
5. **Deploy**

### 3. Heroku (Classic Platform)

1. **Install Heroku CLI** and login
2. **Create a Heroku app**: `heroku create your-app-name`
3. **Add PostgreSQL**: `heroku addons:create heroku-postgresql:mini`
4. **Set environment variables**:
   ```
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set FLASK_ENV=production
   ```
5. **Deploy**: `git push heroku main`

### 4. Fly.io

1. **Install flyctl**: https://fly.io/docs/getting-started/installing-flyctl/
2. **Login**: `fly auth login`
3. **Create app**: `fly launch`
4. **Add secrets**: `fly secrets set SECRET_KEY=your-secret-key`
5. **Deploy**: `fly deploy`

### 5. DigitalOcean App Platform

1. **Create an account** at https://www.digitalocean.com
2. **Create a new App** and connect your repository
3. **Configure:**
   - Build command: `pip install -r requirements.txt`
   - Run command: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:8080 run:app`
   - Add PostgreSQL database
4. **Set environment variables**
5. **Deploy**

## Important Configuration Steps

### 1. Database Setup (Production)

For production, use PostgreSQL instead of SQLite:

1. **Add PostgreSQL driver to requirements.txt**:
   ```
   psycopg2-binary==2.9.9
   ```

2. **Update DATABASE_URL** to use PostgreSQL connection string

3. **Run migrations** (if using Flask-Migrate) or let the app create tables on first run

### 2. Environment Variables

Required environment variables:
- `SECRET_KEY`: A secure random string for Flask session security
- `DATABASE_URL`: Database connection string
- `FLASK_ENV=production`: Set to production mode

Optional:
- `PORT`: Port number (usually set by the platform)

### 3. Static Files and Uploads

- Static files (CSS, JS, images) are served by Flask
- Uploads folder needs to be persistent (use cloud storage for production)
- Consider using AWS S3, Cloudinary, or similar for file uploads in production

### 4. WebSocket Support (Flask-SocketIO)

The app uses Flask-SocketIO for real-time features. Make sure:
- Your hosting platform supports WebSockets
- Eventlet or gevent worker is used (included in Procfile)
- All platforms mentioned above support WebSockets

### 5. Security Checklist

Before deploying:
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use PostgreSQL in production (not SQLite)
- [ ] Set `FLASK_ENV=production`
- [ ] Configure CORS if needed
- [ ] Set up proper file upload limits
- [ ] Consider using a CDN for static files
- [ ] Set up SSL/HTTPS (usually automatic on these platforms)

### 6. File Uploads in Production

For production, consider:
- Using cloud storage (AWS S3, Cloudinary, etc.)
- Setting up proper file size limits
- Implementing file cleanup policies
- Using a reverse proxy like Nginx for better file serving

## Quick Start with Render

1. Push your code to GitHub
2. Go to https://render.com and sign up
3. Click "New +" → "Web Service"
4. Connect your repository
5. Settings:
   - Name: `talentschat` (or your choice)
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app`
6. Add Environment Variables:
   - `SECRET_KEY`: Generate one with `python -c "import secrets; print(secrets.token_hex(32))"`
   - `FLASK_ENV=production`
7. Create PostgreSQL database (if using)
8. Click "Create Web Service"
9. Wait for deployment (usually 2-5 minutes)

Your app will be available at `https://your-app-name.onrender.com`

## Troubleshooting

- **WebSocket errors**: Make sure you're using eventlet worker class
- **Database errors**: Check DATABASE_URL format
- **Import errors**: Ensure all dependencies are in requirements.txt
- **Port errors**: Use `$PORT` environment variable, not hardcoded port
- **Static files not loading**: Check STATIC_URL configuration

## Need Help?

- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- Flask Deployment: https://flask.palletsprojects.com/en/latest/deploying/


