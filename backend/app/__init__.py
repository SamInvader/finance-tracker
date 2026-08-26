from flask import Flask
from .extensions import db, migrate, jwt, cors
from .extensions import token_blocklist


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False, static_folder=None)
    app.config.from_object("backend.config.DevConfig")
    if test_config:
        app.config.update(test_config)

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

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(accounts_bp, url_prefix="/api/accounts")
    app.register_blueprint(tx_bp, url_prefix="/api/transactions")
    app.register_blueprint(categories_bp, url_prefix="/api/categories")
    app.register_blueprint(budgets_bp, url_prefix="/api/budgets")
    app.register_blueprint(goals_bp, url_prefix="/api/goals")

    return app
