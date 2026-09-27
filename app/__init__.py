import os

from flask import Flask

from . import db


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-apteka-secret"),
        DATABASE=os.environ.get("DATABASE", os.path.join(app.instance_path, "apteka.db")),
        # APP_ENV=test włącza endpoint /api/test/reset (reset bazy przed testem)
        APP_ENV=os.environ.get("APP_ENV", "dev"),
        # sztuczne opóźnienie API statystyk -> spinner na dashboardzie (ćwiczenie auto-wait)
        STATS_DELAY_MS=int(os.environ.get("STATS_DELAY_MS", "700")),
        PAGE_SIZE=10,
    )
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    from .auth import bp as auth_bp
    from .dashboard import bp as dashboard_bp
    from .drugs import bp as drugs_bp
    from .sales import bp as sales_bp
    from .api import bp as api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(drugs_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(api_bp)

    from .utils import format_pln

    app.jinja_env.filters["pln"] = format_pln

    return app
