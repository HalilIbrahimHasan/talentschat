# TalentsChat

A Slack-like team collaboration platform built with Flask, featuring real-time chat, file sharing, video uploads, and highlights.

## Features

### MVP Features
- **Authentication**: User registration, login, and password reset (placeholder)
- **Workspaces & Channels**: Create and manage workspaces with public/private channels
- **Real-time Chat**: WebSocket-based messaging with SocketIO
- **Emoji Reactions**: Add reactions (👍 😂 ❤️) to messages
- **Message Highlights & Pins**: Highlight and pin important messages
- **File Uploads**: Upload documents, images, and archives
- **Video Uploads**: Upload and share videos with like functionality
- **Code Snippets**: Share code snippets with syntax highlighting
- **Mobile-Friendly UI**: Responsive design with Tailwind CSS

## Tech Stack

- **Backend**: Flask 3.0
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **ORM**: SQLAlchemy
- **Real-time**: Flask-SocketIO
- **Authentication**: Flask-Login
- **Frontend**: Jinja2 templates + Vanilla JavaScript
- **Styling**: Tailwind CSS (CDN)

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create a virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set environment variables** (optional):
```bash
export SECRET_KEY='your-secret-key-here'
export DATABASE_URL='postgresql://user:pass@localhost/dbname'  # Optional, defaults to SQLite
```

5. **Run the application**:
```bash
python run.py
```

6. **Access the application**:
   - Open your browser and go to `http://localhost:5000`
   - Register a new account or log in
   - Create your first workspace!

## Project Structure

```
talentschat/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration
│   ├── extensions.py        # Flask extensions
│   ├── models/              # Database models
│   ├── blueprints/          # Route blueprints
│   │   ├── auth/           # Authentication
│   │   ├── workspaces/      # Workspace management
│   │   ├── channels/        # Channel management
│   │   ├── chat/            # Chat & SocketIO
│   │   ├── files/           # File uploads
│   │   ├── videos/          # Video features
│   │   └── api/             # JSON API endpoints
│   ├── services/            # Business logic
│   ├── templates/           # Jinja2 templates
│   ├── static/              # CSS, JS, images
│   └── utils/               # Utility functions
├── migrations/              # Database migrations (future)
├── uploads/                 # Uploaded files (created automatically)
├── run.py                   # Application entry point
└── requirements.txt         # Python dependencies
```

## Usage

### Creating a Workspace
1. After logging in, click "Create Workspace"
2. Enter a workspace name
3. You'll be automatically added as the owner

### Creating Channels
1. Navigate to your workspace
2. Click "Create Channel"
3. Choose a name and set it as private (optional)
4. Start chatting!

### Sending Messages
- Type in the message input at the bottom
- Press Enter or click Send
- Messages appear in real-time for all channel members

### Adding Reactions
- Click the reaction button (👍 😂 ❤️) on any message
- Choose an emoji to react

### Highlighting Messages
- Click the "⭐ Highlight" button on any message
- Highlighted messages appear in the right sidebar

### Uploading Files
- Click the paperclip icon in the chat input
- Select files to upload
- Files appear in the Documents page

### Uploading Videos
- Click the paperclip icon and select a video file
- Videos are uploaded and can be viewed in the Videos feed
- Like videos by clicking the heart icon

## Development

### Database
The app uses SQLite by default for development. Tables are created automatically on first run.

For production, set the `DATABASE_URL` environment variable to use PostgreSQL.

### File Storage
Uploads are stored in the `uploads/` directory:
- `uploads/files/` - Documents and images
- `uploads/videos/` - Video files
- `uploads/avatars/` - User avatars (future)

### Security Notes
- Change `SECRET_KEY` in production
- File uploads are validated by extension and size
- CSRF protection is enabled for forms
- Private channels require explicit membership

## Future Enhancements (v1.1)

- Full-text search for messages
- @mentions for users
- Read receipts / last seen
- Notification badges
- Email notifications
- Advanced file previews
- Video comments (partially implemented)

## License

This project is built for educational/demonstration purposes.

## Support

For issues or questions, please check the code comments or create an issue in the repository.

