import os

class Config:
    SECRET_KEY = "finance_project_secret_key_2026"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database", "finance.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False