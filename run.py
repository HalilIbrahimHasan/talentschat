from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("Starting TalentsChat server...")
    print("Server will be available at: http://localhost:8000")
    print("=" * 50)
    socketio.run(app, debug=True, host='0.0.0.0', port=8000, allow_unsafe_werkzeug=True)

