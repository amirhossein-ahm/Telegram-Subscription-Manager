import os

from dotenv import load_dotenv


load_dotenv()


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    API_ID = _get_int("API_ID", 0)
    API_HASH = os.getenv("API_HASH")
    TELEGRAM_SESSION = os.getenv("TELEGRAM_SESSION", "sessions/main")

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database/data.db")

    DEFAULT_MESSAGE_LIMIT = _get_int("DEFAULT_MESSAGE_LIMIT", 300)
    MAX_MESSAGE_LIMIT = _get_int("MAX_MESSAGE_LIMIT", 5000)

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = _get_int("PORT", 5000)
    DEBUG = _get_bool("DEBUG", False)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _get_bool("SESSION_COOKIE_SECURE", False)

    @classmethod
    def validate(cls) -> None:
        required = {
            "SECRET_KEY": cls.SECRET_KEY,
            "API_ID": cls.API_ID,
            "API_HASH": cls.API_HASH,
            "ADMIN_USERNAME": cls.ADMIN_USERNAME,
            "ADMIN_PASSWORD": cls.ADMIN_PASSWORD,
        }

        missing = [key for key, value in required.items() if value in (None, "", 0)]
        if missing:
            raise RuntimeError("Missing environment variables: " + ", ".join(missing))
