import click
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from flask import g
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship


db = SQLAlchemy()
_old_init = db.init_app

class Serializer(object):
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


class Event(db.Model, Serializer):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    location = db.Column(db.String)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

class User(db.Model, Serializer):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, index=True)

class Event2User(db.Model, Serializer):
    __tablename__ = 'event2user'
    id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    user = relationship('User')
    event = relationship('Event')

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@click.command("init-db")
@with_appcontext
def init_db():
    # TODO: init from config
    db.create_all()
    click.echo("Initialized the database")

@click.command("clean-db")
@with_appcontext
def clean_db():
    # TODO: clean from config
    db.drop_all()
    click.echo("cleanup the database")

def init_app(app):
    _old_init(app)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)
    app.cli.add_command(clean_db)

db.init_app = init_app
