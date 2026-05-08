"""Centralized delete password verification for all delete operations."""
from src.config import Settings
from src.helpers.exceptions import ValidationError


def verify_delete_password(password: str) -> None:
    """Verify admin password before allowing delete operations.

    Args:
        password: The password submitted by the user.

    Raises:
        ValidationError: If password is missing or incorrect.

    Returns:
        None if password feature is disabled or password is correct.
    """
    if not Settings.DELETE_PASSWORD_ENABLED:
        return

    if not password:
        raise ValidationError("Admin password is required for delete operations.")

    if password != Settings.DELETE_PASSWORD:
        raise ValidationError("Incorrect admin password.")
