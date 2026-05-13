"""Shared test fixtures for all test modules."""
import os
import sys
import pytest
import tempfile
import shutil

# Ensure project root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope="session")
def app():
    """Create a Flask application configured for testing."""
    # Import here so sys.path is set
    os.environ.setdefault('DATABASE_NAME', 'data/shop.db')
    os.environ.setdefault('SECRET_KEY', 'test-secret-key')
    os.environ.setdefault('LOG_DIR', 'data/logs')
    os.environ.setdefault('MODELS_DIR', 'data/models')
    os.environ.setdefault('UPLOAD_DIR', 'data/shop')
    os.environ.setdefault('DELETE_PASSWORD', 'admin123')
    os.environ.setdefault('DELETE_PASSWORD_ENABLED', 'True')
    os.environ.setdefault('BABEL_DEFAULT_LOCALE', 'bn')
    os.environ.setdefault('BABEL_TRANSLATION_DIRECTORIES', 'data/translations')
    os.environ.setdefault('DATA_DIR', 'data')
    os.environ.setdefault('SHOPS_JSON', 'data/shops.json')
    os.environ.setdefault('ODT_FILE', 'shop_details.odt')
    os.environ.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', 'False')
    os.environ.setdefault('APP_ENV', 'testing')

    from main import app as flask_app
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    return flask_app


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_client(app):
    """Create an authenticated Flask test client (admin session)."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['is_admin'] = True
        yield client


@pytest.fixture
def app_context(app):
    """Push an application context for DB operations."""
    with app.app_context():
        yield app
