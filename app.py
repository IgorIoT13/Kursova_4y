import os
from flask import Flask
from config import config
from models import db
from routes import register_routes
from typing import Optional
import pymysql


def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure the physical database exists (create if missing) before initializing SQLAlchemy
    def ensure_database_exists(app):
        cfg = app.config
        db_name = cfg.get('DB_NAME')
        host = cfg.get('DB_HOST', 'localhost')
        port = int(cfg.get('DB_PORT', 3306))
        user = cfg.get('DB_USER', '')
        password = cfg.get('DB_PASSWORD', '')

        # Use PyMySQL to connect to the server (without selecting a database)
        try:
            conn = pymysql.connect(host=host, port=port, user=user, password=password, charset='utf8mb4')
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            conn.commit()
            conn.close()
        except Exception:
            # Re-raise so startup fails loudly if DB server is unreachable or credentials are wrong
            raise

    ensure_database_exists(app)

    # Initialize extensions
    db.init_app(app)
    
    # Optional: run precondition loader if explicitly enabled via env var
    if os.environ.get('PRECONDITION_AUTOLOAD', '').lower() in ('1', 'true', 'yes'):
        try:
            from precondition.load_sample import load_sample
            with app.app_context():
                print('Running precondition autoload...')
                load_sample()
        except Exception as e:
            # don't fail app startup for precondition; surface a warning
            print('Precondition autoload failed:', e)

    # Register routes
    register_routes(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app()
    # Note: Change host to '127.0.0.1' in production and disable debug mode
    app.run(host='0.0.0.0', port=5000)
