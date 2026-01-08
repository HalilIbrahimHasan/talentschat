from app import create_app
from app.extensions import socketio
import os

app = create_app()

# This is for local development
# For production, use: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print("=" * 50)
    print("Starting TalentsChat server...")
    print(f"Server will be available at: http://localhost:{port}")
    print(f"Debug mode: {debug}")
    print("=" * 50)
    socketio.run(app, debug=debug, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)

