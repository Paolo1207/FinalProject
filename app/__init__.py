import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_login import LoginManager

cache = Cache()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(os.path.dirname(basedir), 'instance', 'rice_inventory.db')

    app.config.from_mapping(
        SECRET_KEY='your-secret-key',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CACHE_TYPE='SimpleCache',
        CACHE_DEFAULT_TIMEOUT=900,
    )

    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'

    # Import models here *after* db init_app to avoid circular imports
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register blueprints here
    from app.auth import auth
    from app.routes import main

    app.register_blueprint(auth)
    app.register_blueprint(main)

    return app
