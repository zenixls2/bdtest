from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bdtest.db'
db = SQLAlchemy(app)

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
    user = relationship("User")
    event = relationship("Event")

#db.drop_all()
db.create_all()

@app.route("/")
def hello():
    return "Hello World"

@app.route("/listall")
def listall():
    return jsonify(Serializer.serialize_list(Event.query.all()))

# http://localhost:5000/add_event?name=xdd&location=tw&start_time=2020/12/18-12:30:00&end_time=2020/12/31-12:30:00
@app.route("/add_event")
def add_event():
    name = request.args.get("name")
    location = request.args.get("location")
    start_time = datetime.strptime(request.args.get("start_time"), "%Y/%m/%d-%H:%M:%S")
    end_time = datetime.strptime(request.args.get("end_time"), "%Y/%m/%d-%H:%M:%S")
    event = Event(name=name, location=location, start_time=start_time, end_time=end_time)
    try:
        db.session.add(event)
        db.session.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return jsonify({"status": "Error", "msg": error})
    return jsonify({"status": "Ok", "id": event.id})

@app.route("/add_user")
def add_user():
    email = request.args.get("email")
    user = User(email=email)
    try:
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return jsonify({"status": "Error", "msg": error})

    return jsonify({"status": "OK", "user_id": user.user_id})

@app.route("/sign_event")
def sign_event():
    uid = request.args.get("user_id")
    id = request.args.get("id")
    e2u = Event2User(id=id, user_id=uid)
    try:
        if None == db.session.query(User, Event).filter(User.user_id == uid).filter(Event.id == id).first():
            return jsonify({"status": "Error", "msg": "Both the event and user should exist"})
        db.session.add(e2u)
        db.session.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return jsonify({"status": "Error", "msg": error})

    return jsonify({"status": "Ok"})

@app.route("/unsign_event")
def unsign_event():
    email = request.args.get("email")
    id = request.args.get("id")
    if id == None or email == None:
        return jsonify({"status": "Error", "msg": "should provide both email and event id"})
    try:
        e2u = db.session.query(Event2User).filter(Event2User.user_id == User.user_id, User.email == email).first()
        if e2u != None:
            db.session.delete(e2u)
            db.session.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return jsonify({"status": "Error", "msg": error})

    return jsonify({"status": "Ok"})

@app.route("/get_user")
def get_user():
    email = request.args.get("email")
    if email != None:
        user = db.session.query(User).filter(User.email == email).first()
        if user == None:
            return jsonify({"status": "Error", "msg": "No such user"})
        eids = [eid[0] for eid in db.session.query(Event2User.id).filter(Event2User.user_id == user.user_id)]
        return jsonify({"status": "Ok", "user": user.serialize(), "events": eids})
    uid = request.args.get("user_id")
    if uid != None:
        user = db.session.query(User).filter(User.user_id == uid).first()
        if user == None:
            return jsonify({"status": "Error", "msg": "No such user"})

        eids = [eid[0] for eid in db.session.query(Event2User.id).filter(Event2User.user_id == uid)]
        return jsonify({"status": "Ok", "user": user.serialize(), "events": eids})
    return jsonify({"status": "Error", "msg": "No limitation"})


@app.route("/get_event")
def get_event():
    id = request.args.get('id')
    event = db.session.query(Event).filter(Event.id == id).first()
    if event == None:
        return jsonify({"status": "Error", "msg": "No such event"})
    emails = [email[0] for email in db.session.query(User.email).filter(Event2User.id == id).filter(User.user_id == Event2User.user_id)]
    return jsonify({"status": "Ok", "event": event.serialize(), "users": emails}) 

