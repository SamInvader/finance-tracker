"""Application factory for the finance tracker backend."""

import sys
from pathlib import Path

from flask import Flask

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .extensions import db, migrate, jwt, cors, token_blocklist


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False, static_folder=None)
    try:
        app.config.from_object("backend.config.DevConfig")
    except (ImportError, ModuleNotFoundError):
        app.config.from_object("config.DevConfig")
    if test_config:
        if isinstance(test_config, str):
            app.config.from_object(test_config)
        else:
            app.config.from_object(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # token blocklist (simple in-memory revocation)
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload.get("jti")
        return jti in token_blocklist

    # register blueprints
    from .routes.auth import auth_bp
    from .routes.accounts import accounts_bp
    from .routes.transactions import tx_bp
    from .routes.categories import categories_bp
    from .routes.budgets import budgets_bp
    from .routes.goals import goals_bp
    from .routes.analytics import bp as analytics_bp
    from .routes.wealth import bp as wealth_bp
    from .routes.planning import bp as planning_bp
    from .routes.data import bp as data_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(accounts_bp, url_prefix="/api/accounts")
    app.register_blueprint(tx_bp, url_prefix="/api/transactions")
    app.register_blueprint(categories_bp, url_prefix="/api/categories")
    app.register_blueprint(budgets_bp, url_prefix="/api/budgets")
    app.register_blueprint(goals_bp, url_prefix="/api/goals")
    app.register_blueprint(analytics_bp, url_prefix="/api")
    app.register_blueprint(wealth_bp, url_prefix="/api")
    app.register_blueprint(planning_bp, url_prefix="/api")
    app.register_blueprint(data_bp, url_prefix="/api")

    @app.get("/api/health")
    def health():
        return {"ok": True, "service": "ledgerly"}

    @app.get("/")
    def index():
        return {"ok": True, "service": "ledgerly", "message": "API is running"}

    return app
