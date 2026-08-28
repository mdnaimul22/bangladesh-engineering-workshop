"""Synthetic test case to verify the password-protected delete pipeline."""
import os
import pytest

# Set required environment variables
os.environ['SECRET_KEY'] = 'test-secret'
os.environ['APP_HOST'] = '127.0.0.1'
os.environ['APP_PORT'] = '5000'
os.environ['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
os.environ['BABEL_DEFAULT_LOCALE'] = 'bn'
os.environ['BABEL_TRANSLATION_DIRECTORIES'] = 'data/translations'
os.environ['DATABASE_NAME'] = 'data/shop.db'
os.environ['DELETE_PASSWORD'] = 'admin123'
os.environ['DELETE_PASSWORD_ENABLED'] = 'True'
os.environ['ADMIN_USERNAME'] = 'admin'
os.environ['ADMIN_PASSWORD'] = 'adminpass'
os.environ['BUSINESS_NAME'] = 'BEW'
os.environ['BUSINESS_DESC'] = 'Desc'
os.environ['BUSINESS_ADDRESS'] = 'Dhaka'
os.environ['BUSINESS_PHONE'] = '01700000000'
os.environ['BUSINESS_EMAIL'] = 'info@bew.com'
os.environ['BUSINESS_MAP_URL'] = 'https://maps.google.com'
os.environ['BUSINESS_OPENING_HOURS'] = '9am-6pm'
os.environ['BUSINESS_OPEN_TIME'] = '09:00'
os.environ['BUSINESS_CLOSE_TIME'] = '18:00'
os.environ['BUSINESS_LATITUDE'] = '23.8103'
os.environ['BUSINESS_LONGITUDE'] = '90.4125'
os.environ['LOG_DIR'] = 'data/logs'
os.environ['MODELS_DIR'] = 'data/models'
os.environ['UPLOAD_DIR'] = 'data/shop'
os.environ['DATA_DIR'] = 'data'
os.environ['SHOPS_JSON'] = 'data/shops.json'
os.environ['ODT_FILE'] = 'shop_details.odt'

from src.helpers.auth import verify_delete_password
from src.helpers.exceptions import ValidationError


class TestDeletePasswordPipeline:
    """Synthetic unit test suite verifying the delete password pipeline logic."""

    def test_pipeline_with_correct_password(self):
        """Correct admin password passes verification without raising exception."""
        # Should pass smoothly
        verify_delete_password('admin123')

    def test_pipeline_with_wrong_password(self):
        """Wrong password raises ValidationError."""
        with pytest.raises(ValidationError, match="Incorrect admin password"):
            verify_delete_password('invalid_pass')

    def test_pipeline_with_empty_password(self):
        """Empty password (such as submitted by standard forms without modal) raises ValidationError."""
        with pytest.raises(ValidationError, match="Admin password is required"):
            verify_delete_password('')
