from flask import Flask
from app.extensions import db, login_manager, socketio, csrf
from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure SQLAlchemy engine options for eventlet compatibility
    from sqlalchemy.pool import NullPool
    import os
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if database_url.startswith('sqlite'):
        # For SQLite with eventlet, use NullPool to avoid threading issues
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'poolclass': NullPool,
            'connect_args': {'check_same_thread': False}
        }
    else:
        # For PostgreSQL, use pool settings compatible with eventlet
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 3600,
        }
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    csrf.init_app(app)
    
    # Register blueprints
    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.blueprints.workspaces import bp as workspaces_bp
    app.register_blueprint(workspaces_bp, url_prefix='/w')
    
    from app.blueprints.channels import bp as channels_bp
    app.register_blueprint(channels_bp, url_prefix='/w/<workspace_slug>/c')
    
    from app.blueprints.chat import bp as chat_bp
    app.register_blueprint(chat_bp, url_prefix='/w/<workspace_slug>/c/<channel_slug>')
    
    from app.blueprints.files import bp as files_bp
    app.register_blueprint(files_bp, url_prefix='/w/<workspace_slug>/files')
    
    from app.blueprints.videos import bp as videos_bp
    app.register_blueprint(videos_bp)
    
    from app.blueprints.articles import bp as articles_bp
    app.register_blueprint(articles_bp)
    
    from app.blueprints.profile import bp as profile_bp
    app.register_blueprint(profile_bp, url_prefix='/profile')
    
    from app.blueprints.api import bp as api_bp
    # Exempt API routes from CSRF (they use JSON)
    csrf.exempt(api_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Import socket events
    from app.blueprints.chat import sockets
    
    # Setup login manager
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    # Make CSRF token available in templates
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)
    
    # Root route
    @app.route('/')
    def index():
        from flask_login import current_user
        from flask import render_template, redirect, url_for
        if current_user.is_authenticated:
            return redirect(url_for('workspaces.dashboard'))
        return render_template('landing.html')
    
    # Create tables and migrate schema
    with app.app_context():
        db.create_all()
        
        # Migrate existing tables (SQLite-specific migrations)
        # Only run if using SQLite, skip for PostgreSQL
        database_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if database_url.startswith('sqlite'):
            try:
                from sqlalchemy import text
                conn = db.engine.connect()
                
                # Check if is_public column exists
                result = conn.execute(text("PRAGMA table_info(workspaces)"))
                columns = [row[1] for row in result]
                
                if 'is_public' not in columns:
                    conn.execute(text("ALTER TABLE workspaces ADD COLUMN is_public BOOLEAN DEFAULT 1"))
                    conn.commit()
                    print("Added is_public column to workspaces")
                
                if 'invite_code' not in columns:
                    conn.execute(text("ALTER TABLE workspaces ADD COLUMN invite_code VARCHAR(20)"))
                    conn.commit()
                    print("Added invite_code column to workspaces")
                    
                    # Generate invite codes for existing workspaces
                    from app.models.workspace import Workspace
                    from app.utils.ids import generate_invite_code
                    workspaces = Workspace.query.filter(Workspace.invite_code == None).all()
                    for ws in workspaces:
                        ws.invite_code = generate_invite_code()
                    db.session.commit()
                    print(f"Generated invite codes for {len(workspaces)} existing workspaces")
                
                # Migrate videos table to add new columns
                try:
                    result = conn.execute(text("PRAGMA table_info(videos)"))
                    video_columns = [row[1] for row in result]
                    
                    if 'external_url' not in video_columns:
                        conn.execute(text("ALTER TABLE videos ADD COLUMN external_url VARCHAR(500)"))
                        conn.commit()
                        print("Added external_url column to videos")
                    
                    if 'video_type' not in video_columns:
                        conn.execute(text("ALTER TABLE videos ADD COLUMN video_type VARCHAR(20) DEFAULT 'upload'"))
                        conn.commit()
                        print("Added video_type column to videos")
                except Exception as ve:
                    print(f"Video migration note: {ve}")
                
                # Migrate users table to add profile fields
                try:
                    result = conn.execute(text("PRAGMA table_info(users)"))
                    user_columns = [row[1] for row in result]
                    
                    if 'profile_image' not in user_columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN profile_image VARCHAR(255)"))
                        conn.commit()
                        print("Added profile_image column to users")
                    
                    if 'bio' not in user_columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN bio TEXT"))
                        conn.commit()
                        print("Added bio column to users")
                except Exception as ue:
                    print(f"User migration note: {ue}")
                
                conn.close()
            except Exception as e:
                print(f"Migration note: {e}")
                # If migration fails, tables might not exist yet - that's okay
    
    return app
