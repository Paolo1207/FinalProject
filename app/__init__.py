import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Determine absolute path to the SQLite database file in the instance folder
    basedir = os.path.abspath(os.path.dirname(__file__))  # points to /app
    db_path = os.path.join(os.path.dirname(basedir), 'instance', 'rice_inventory.db')  # one level up + /instance/rice_inventory.db
    
    app.config.from_mapping(
        SECRET_KEY='your-secret-key',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import main
    app.register_blueprint(main)

    return app
