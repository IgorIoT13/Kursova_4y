"""User-related routes."""
from flask import jsonify
from models import db, User


def user_routes(app):
    """Register user-related routes."""
    
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
