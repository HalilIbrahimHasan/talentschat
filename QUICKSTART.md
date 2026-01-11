# Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Run the Application

```bash
python run.py
```

The application will start on `http://localhost:5000`

## 3. First Steps

1. **Register an Account**
   - Go to `http://localhost:5000`
   - Click "Register" or go to `/auth/register`
   - Fill in your name, email, and password

2. **Create a Workspace**
   - After logging in, you'll see the workspace dashboard
   - Click "Create Workspace"
   - Enter a workspace name
   - A "general" channel will be created automatically

3. **Start Chatting**
   - Click on your workspace
   - Click on the "general" channel
   - Type a message and press Enter!

## 4. Try These Features

- **Create a Channel**: Click "Create Channel" in your workspace
- **Upload Files**: Click the paperclip icon in chat
- **Add Reactions**: Click the reaction button (👍 😂 ❤️) on any message
- **Highlight Messages**: Click "⭐ Highlight" on important messages
- **Upload Videos**: Upload a video file and it will appear in the Videos feed
- **Like Videos**: Click the heart icon on videos

## 5. Mobile View

The app is responsive! Try resizing your browser or opening on a mobile device to see the mobile-friendly layout.

## Troubleshooting

### Database Issues
If you see database errors, delete `app.db` and restart the app. Tables will be recreated automatically.

### Port Already in Use
If port 5000 is busy, edit `run.py` and change the port number.

### Upload Errors
Make sure the `uploads/` directory exists and is writable. It should be created automatically.

## Next Steps

- Invite team members to your workspace
- Create private channels for specific teams
- Upload and share documents
- Build your video library

Enjoy using TalentsChat! 🚀


