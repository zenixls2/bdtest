'''
Defile db tables and init scripts
'''

import click
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from flask import g
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship


db = SQLAlchemy()
_old_init = db.init_app

class Serializer:
    '''Util for making models json serializable'''
    def serialize(self):
        '''for json serialize, we provide a dict'''
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(i):
        '''serialize util for list of objects'''
        return [j.serialize() for j in i]


class Event(db.Model, Serializer):
    '''Event table defintion'''
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    location = db.Column(db.String)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

class User(db.Model, Serializer):
    '''User table defintion'''
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, index=True)

class Event2User(db.Model, Serializer):
    '''Event to User relationship'''
    __tablename__ = 'event2user'
    id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    user = relationship('User')
    event = relationship('Event')

def close_db(_=None):
    '''Turn off db connection'''
    database = g.pop('db', None)
    if database is not None:
        database.close()

@click.command("init-db")
@with_appcontext
def init_db():
    ''' init db tables'''
    # TODO: init from config
    db.create_all()
    click.echo("Initialized the database")

@click.command("clean-db")
@with_appcontext
def clean_db():
    '''remove everything from db'''
    # TODO: clean from config
    db.drop_all()
    click.echo("cleanup the database")

def init_app(app):
    '''for adding commands'''
    _old_init(app)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)
    app.cli.add_command(clean_db)

db.init_app = init_app
