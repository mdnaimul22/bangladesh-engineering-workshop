"""Tests for src/config — Settings initialization and parameter resolution."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestConfigInit:
    """Verify config module loads and exposes all expected symbols."""

    def test_config_imports(self):
        """All public names from __init__.py should be importable."""
        from src.config import (
            PROJECT_ROOT, find_project_root,
            read_text, write_text, read_json, write_json,
            read_pickle, write_pickle,
            exists, ensure_dir, delete, list_files, get_abs_path,
            load_dotenv, set_value, get_value, remove_value,
            Settings, setup_logger,
        )
        assert Settings is not None
        assert callable(setup_logger)
        assert callable(read_pickle)
        assert callable(write_pickle)

    def test_project_root_exists(self):
        """PROJECT_ROOT should point to an existing directory."""
        from src.config import PROJECT_ROOT
        assert PROJECT_ROOT.exists()
        assert PROJECT_ROOT.is_dir()

    def test_find_project_root_returns_path(self):
        """find_project_root() should return a Path object."""
        from src.config import find_project_root
        root = find_project_root()
        assert root.exists()


class TestSettings:
    """Verify Settings fields resolve correctly from .env."""

    def test_settings_instance(self):
        """Settings should instantiate without errors."""
        from src.config import Settings
        assert Settings is not None

    def test_database_url_format(self):
        """DATABASE_URL should be a sqlite URI."""
        from src.config import Settings
        assert Settings.DATABASE_URL.startswith('sqlite:///')

    def test_upload_dir_is_path(self):
        """UPLOAD_DIR should be a Path object."""
        from src.config import Settings
        from pathlib import Path
        assert isinstance(Settings.UPLOAD_DIR, Path)

    def test_models_dir_is_path(self):
        """MODELS_DIR should be a Path object."""
        from src.config import Settings
        from pathlib import Path
        assert isinstance(Settings.MODELS_DIR, Path)

    def test_log_dir_is_path(self):
        """LOG_DIR should be a Path object."""
        from src.config import Settings
        from pathlib import Path
        assert isinstance(Settings.LOG_DIR, Path)

    def test_secret_key_not_empty(self):
        """SECRET_KEY must not be empty."""
        from src.config import Settings
        assert Settings.SECRET_KEY
        assert len(Settings.SECRET_KEY) > 0

    def test_delete_password_setting(self):
        """DELETE_PASSWORD should exist in Settings."""
        from src.config import Settings
        assert hasattr(Settings, 'DELETE_PASSWORD')

    def test_babel_locale(self):
        """BABEL_DEFAULT_LOCALE should be 'bn' or 'en'."""
        from src.config import Settings
        assert Settings.BABEL_DEFAULT_LOCALE in ('bn', 'en')

    def test_subdirectories_resolve(self):
        """Upload sub-dirs should resolve from Settings."""
        from src.config import Settings
        assert Settings.SALES_VOUCHER_DIR is not None
        assert Settings.PURCHASE_VOUCHER_DIR is not None
        assert Settings.WORK_ORDER_DIR is not None
        assert Settings.GALLERY_DIR is not None


class TestLogger:
    """Verify logger setup works."""

    def test_setup_logger_returns_logger(self):
        """setup_logger should return a logging.Logger."""
        import logging
        from src.config import setup_logger, Settings
        logger = setup_logger(Settings.LOG_DIR / "test.log", name="test.logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.logger"


class TestFiles:
    """Verify file utility functions."""

    def test_exists_on_real_file(self):
        """exists() should return True for .env."""
        from src.config import exists
        assert exists('.env') is True

    def test_exists_on_missing_file(self):
        """exists() should return False for non-existent file."""
        from src.config import exists
        assert exists('nonexistent_file_xyz.txt') is False

    def test_get_abs_path(self):
        """get_abs_path() should return absolute string."""
        from src.config import get_abs_path
        result = get_abs_path('src', 'config')
        assert os.path.isabs(result)
        assert 'src' in result
