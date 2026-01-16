"""Routes package."""
from routes.main import main_routes

__all__ = ['main_routes']


def register_routes(app):
    """Register all application routes."""
    main_routes(app)
