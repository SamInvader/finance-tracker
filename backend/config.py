import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    db_path = os.path.join(basedir, 'instance', 'finance.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{db_path}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    DEBUG = True


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProdConfig(Config):
    DEBUG = False


class DemoConfig(Config):
    DEBUG = True
