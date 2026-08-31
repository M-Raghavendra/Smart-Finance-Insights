import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    default_db_path = os.path.join(BASE_DIR, "database", "finance.db").replace("\\", "/")

    env_db_url = os.getenv("DATABASE_URL")
    if env_db_url and env_db_url.startswith("sqlite:///") and not env_db_url.startswith("sqlite:////") and not (len(env_db_url) > 11 and env_db_url[10] == ":"):
        rel_path = env_db_url.replace("sqlite:///", "")
        abs_db_path = os.path.abspath(os.path.join(BASE_DIR, rel_path)).replace("\\", "/")
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{abs_db_path}"
    else:
        SQLALCHEMY_DATABASE_URI = env_db_url or f"sqlite:///{default_db_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session Security Settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1", "yes")