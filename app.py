import os
from flask import Flask, jsonify
from config import config
from models import db, User


def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Register routes
    register_routes(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app


def register_routes(app):
    """Register application routes."""
    
    @app.route('/')
    def index():
        """Index route."""
        return jsonify({
            'message': 'Welcome to Flask App with MySQL',
            'status': 'running'
        })
    
    @app.route('/health')
    def health():
        """Health check route."""
        try:
            # Test database connection
            db.session.execute(db.text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return jsonify({
            'status': 'healthy',
            'database': db_status
        })
    
    @app.route('/users')
    def get_users():
        """Get all users."""
        try:
            users = User.query.all()
            return jsonify({
                'users': [user.to_dict() for user in users],
                'count': len(users)
            })
        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500
    
    @app.route('/users/create/<username>/<email>')
    def create_user(username, email):
        """Create a new user (for testing purposes)."""
        try:
            user = User(username=username, email=email)
            db.session.add(user)
            db.session.commit()
            return jsonify({
                'message': 'User created successfully',
                'user': user.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'error': str(e)
            }), 500


if __name__ == '__main__':
    app = create_app()
    # Note: Change host to '127.0.0.1' in production and disable debug mode
    app.run(host='0.0.0.0', port=5000)
