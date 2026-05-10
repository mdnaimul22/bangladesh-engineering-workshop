from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from .paths import PROJECT_ROOT

class Settings(BaseSettings):
    PROJECT_NAME: str = "bew"
    VERSION: str = "1.0.0"
    ENV: str = Field(default="development", validation_alias="APP_ENV")

    # Flask configurations
    SECRET_KEY: str = Field(..., validation_alias="SECRET_KEY")
    APP_HOST: str = Field(..., validation_alias="APP_HOST")
    APP_PORT: int = Field(..., validation_alias="APP_PORT")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = Field(..., validation_alias="SQLALCHEMY_TRACK_MODIFICATIONS")
    BABEL_DEFAULT_LOCALE: str = Field(..., validation_alias="BABEL_DEFAULT_LOCALE")
    BABEL_TRANSLATION_DIRECTORIES: str = Field(..., validation_alias="BABEL_TRANSLATION_DIRECTORIES")

    # Database
    DATABASE_NAME: str = Field(..., validation_alias="DATABASE_NAME")
    DELETE_PASSWORD: str = Field(..., validation_alias="DELETE_PASSWORD")
    DELETE_PASSWORD_ENABLED: bool = Field(..., validation_alias="DELETE_PASSWORD_ENABLED")

    # Admin Login
    ADMIN_USERNAME: str = Field(default="admin", validation_alias="ADMIN_USERNAME")
    ADMIN_PASSWORD: str = Field(default="admin", validation_alias="ADMIN_PASSWORD")

    # Business Info for SEO
    BUSINESS_NAME: str = Field(..., validation_alias="BUSINESS_NAME")
    BUSINESS_DESC: str = Field(..., validation_alias="BUSINESS_DESC")
    BUSINESS_ADDRESS: str = Field(..., validation_alias="BUSINESS_ADDRESS")
    BUSINESS_PHONE: str = Field(..., validation_alias="BUSINESS_PHONE")
    BUSINESS_EMAIL: str = Field(..., validation_alias="BUSINESS_EMAIL")
    BUSINESS_MAP_URL: str = Field(..., validation_alias="BUSINESS_MAP_URL")
    BUSINESS_OPENING_HOURS: str = Field(..., validation_alias="BUSINESS_OPENING_HOURS")
    BUSINESS_OPEN_TIME: str = Field(..., validation_alias="BUSINESS_OPEN_TIME")
    BUSINESS_CLOSE_TIME: str = Field(..., validation_alias="BUSINESS_CLOSE_TIME")
    BUSINESS_LATITUDE: float = Field(..., validation_alias="BUSINESS_LATITUDE")
    BUSINESS_LONGITUDE: float = Field(..., validation_alias="BUSINESS_LONGITUDE")

    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite:///{PROJECT_ROOT / self.DATABASE_NAME}"

    # Directories (optional — have sensible defaults relative to project root)
    log_dir_rel: str = Field(..., validation_alias="LOG_DIR")
    models_dir_rel: str = Field(..., validation_alias="MODELS_DIR")
    upload_dir_rel: str = Field(..., validation_alias="UPLOAD_DIR")
    data_dir_rel: str = Field(..., validation_alias="DATA_DIR")

    # Files
    shops_json_rel: str = Field(..., validation_alias="SHOPS_JSON")
    odt_file_rel: str = Field(..., validation_alias="ODT_FILE")

    def _resolve(self, val: str) -> Path:
        p = Path(val).expanduser()
        return p if p.is_absolute() else PROJECT_ROOT / p

    @property
    def LOG_DIR(self) -> Path: return self._resolve(self.log_dir_rel)

    @property
    def MODELS_DIR(self) -> Path: return self._resolve(self.models_dir_rel)

    @property
    def UPLOAD_DIR(self) -> Path: return self._resolve(self.upload_dir_rel)

    @property
    def DATA_DIR(self) -> Path: return self._resolve(self.data_dir_rel)

    @property
    def SHOPS_JSON_PATH(self) -> Path: return self._resolve(self.shops_json_rel)

    @property
    def ODT_FILE_PATH(self) -> Path: return self._resolve(self.odt_file_rel)

    @property
    def EXTRACTED_ODT_DIR(self) -> Path: return self.DATA_DIR / "extracted_odt"

    @property
    def SALES_VOUCHER_DIR(self) -> Path: return self.UPLOAD_DIR / "sales_voucher"

    @property
    def PURCHASE_VOUCHER_DIR(self) -> Path: return self.UPLOAD_DIR / "purchase_voucher"

    @property
    def WORK_ORDER_DIR(self) -> Path: return self.UPLOAD_DIR / "work_orders"

    @property
    def GALLERY_DIR(self) -> Path: return self.UPLOAD_DIR / "gallery"

    @property
    def is_production(self) -> bool: return self.ENV.lower() == "production"

    @property
    def is_development(self) -> bool: return self.ENV.lower() == "development"

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

Settings = Settings()
