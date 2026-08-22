import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
DATABASE_PATH = os.path.join(INSTANCE_DIR, "finance_tracker.db")
