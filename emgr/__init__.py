from flask import Flask
import os

def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SQLALCHEMY_DATABASE_URI='sqlite:///' +
                os.path.join(app.instance_path, "bdtest.db"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(config)
    
    from emgr.model import db
    db.init_app(app)

    from emgr import methods
    app.register_blueprint(methods.bp)

    return app
