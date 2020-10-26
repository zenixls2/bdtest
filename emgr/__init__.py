from flask import Flask
import os

def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SQLALCHEMY_DATABASE_URI='sqlite:///' +
                os.path.join(app.instance_path, "bdtest.db"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            MAIL_SERVER='smtp.googlemail.com',
            MAIL_PORT=587,
            MAIL_USE_TLS=True,
            MAIL_USERNAME='zenixls2@gmail.com',
            MAIL_DEFAULT_SENDER='zenixls2@gmail.com',
            MAIL_PASSWORD='password', # fake one
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
    methods.mail.init_app(app)
    app.register_blueprint(methods.bp)

    return app
