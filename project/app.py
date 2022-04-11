from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from project.config import DevConfig, TestConfig

db = SQLAlchemy()
migrate = Migrate()

def create_app(testing=False):
    app = Flask(__name__)
    conf = TestConfig() if testing else DevConfig()
    app.config.from_object(conf)
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    from project.routes import api as main_blueprint
    app.register_blueprint(main_blueprint)
    return app

