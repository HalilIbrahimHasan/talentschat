# TalentsChat

A real-time chat application built with Flask, featuring workspaces, channels, video calls, file sharing, and more.

## Features

- 🔐 User authentication and authorization
- 👥 Workspaces and channels management
- 💬 Real-time messaging with SocketIO
- 📹 Video and audio calling with screen sharing
- 📁 File and document sharing
- 🎥 Video uploads and playback
- 📝 Articles/blog system
- 👤 User profiles with badges and ratings
- ⭐ Emoji reactions and message highlighting
- 📊 Online user presence

## Tech Stack

- **Backend**: Flask, Flask-SocketIO, SQLAlchemy
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Database**: SQLite (development) / PostgreSQL (production)
- **Real-time**: WebSockets via SocketIO
- **Video Calls**: WebRTC

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd talentschat
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and set SECRET_KEY
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   - Open http://localhost:8000 in your browser

## Deployment

This application is ready for deployment on various platforms. **Netlify is NOT suitable** for Flask applications.

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy Options:

- **Render.com** (Recommended - Free tier available)
- **Railway.app** (Easy setup)
- **Heroku** (Classic platform)
- **Fly.io** (Modern alternative)
- **DigitalOcean App Platform**

## Configuration

### Environment Variables

- `SECRET_KEY`: Flask secret key for sessions (required in production)
- `DATABASE_URL`: Database connection string
- `FLASK_ENV`: Set to `production` for production deployment
- `PORT`: Server port (default: 8000)

### Database

- **Development**: SQLite (app.db)
- **Production**: PostgreSQL (recommended)

To use PostgreSQL, add `psycopg2-binary` to requirements.txt (already included) and set `DATABASE_URL` to your PostgreSQL connection string.

## Project Structure

```
talentschat/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   ├── extensions.py        # Flask extensions
│   ├── blueprints/          # Application blueprints
│   ├── models/              # Database models
│   ├── templates/           # HTML templates
│   ├── static/              # Static files (CSS, JS, images)
│   ├── services/            # Business logic services
│   └── utils/               # Utility functions
├── uploads/                 # User uploads (not in git)
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── DEPLOYMENT.md            # Deployment guide
```

## Development

### Running in Development Mode

```bash
python run.py
```

The app will run with debug mode enabled on http://localhost:8000

### Adding New Features

- Blueprints go in `app/blueprints/`
- Models go in `app/models/`
- Templates go in `app/templates/`
- Static files go in `app/static/`

## License

[Your License Here]

## Support

For deployment help, see [DEPLOYMENT.md](DEPLOYMENT.md)
