import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache

cache = Cache()
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    basedir = os.path.abspath(os.path.dirname(__file__))  # /app
    db_path = os.path.join(os.path.dirname(basedir), 'instance', 'rice_inventory.db')
    
    app.config.from_mapping(
        SECRET_KEY='your-secret-key',  # Replace with a secure key in production
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CACHE_TYPE='SimpleCache',
        CACHE_DEFAULT_TIMEOUT=900,
    )

    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    return app
