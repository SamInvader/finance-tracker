import os
from flask import Flask

from config import BASE_DIR
from finance_tracker.database import init_db


def create_app():
    app = Flask(__name__, instance_relative_config=True, template_folder=os.path.join(BASE_DIR, "templates"), static_folder=os.path.join(BASE_DIR, "static"))
    app.config.from_object("config")

    os.makedirs(app.instance_path, exist_ok=True)
    init_db()

    from finance_tracker.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app
