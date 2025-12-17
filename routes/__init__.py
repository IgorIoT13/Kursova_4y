"""Routes package."""
from routes.main import main_routes
from routes.user_routes import user_routes

__all__ = ['main_routes', 'user_routes']


def register_routes(app):
    """Register all application routes."""
    main_routes(app)
    user_routes(app)
