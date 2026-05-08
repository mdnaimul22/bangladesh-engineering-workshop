"""File upload helper for vouchers, visiting cards, and work order documents."""
import os
from pathlib import Path
from werkzeug.utils import secure_filename

from src.config import Settings, setup_logger

logger = setup_logger(Settings.LOG_DIR / "helpers.log", name="bew.helpers.upload")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}


def allowed_file(filename: str) -> bool:
    """Check if the file extension is in the allowed set."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file, subfolder: str, custom_name: str | None = None) -> str | None:
    """Save an uploaded file to the specified subfolder under UPLOAD_DIR.

    Args:
        file: The uploaded file object from request.files.
        subfolder: Subdirectory name (e.g. 'purchase_voucher', 'visiting_card').
        custom_name: Optional custom filename (without extension).

    Returns:
        The relative file path from UPLOAD_DIR, or None if no valid file.
    """
    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        logger.warning(f"Rejected upload: {file.filename} (not in allowed extensions)")
        return None

    filename = secure_filename(file.filename)
    if custom_name:
        ext = filename.rsplit('.', 1)[1].lower()
        filename = f"{secure_filename(custom_name)}.{ext}"

    upload_dir = Path(Settings.UPLOAD_DIR) / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / filename
    file.save(str(file_path))
    logger.info(f"Saved upload: {file_path}")

    return f"{subfolder}/{filename}"
