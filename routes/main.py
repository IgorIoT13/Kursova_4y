"""Main application routes."""
from flask import jsonify
from models import db


def main_routes(app):
    """Register main application routes."""
    
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
