from flask import Blueprint, request, jsonify
from flask import g
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from emgr.model import db, Serializer, Event, User, Event2User

bp = Blueprint("methods", __name__)

DATE_FORMAT = "%Y/%m/%d-%H:%M:%S"

def handle_error(e):
    error = str(e.__dict__.get('orig') or 'error orig unknown')
    return jsonify({"status": "Error", "msg": error})

def handle_error_str(e):
    return jsonify({"status": "Error", "msg": e})

def handle_ok(content=None):
    content = content or {}
    return jsonify({"status": "Ok", **content})

@bp.route("/")
def index():
    return "Hello world"


@bp.route("/listall")
def listall():
    return jsonify(Serializer.serialize_list(Event.query.all()))


@bp.route("/add_event")
def add_event():
    name = request.args.get("name")
    location = request.args.get("location")
    start_time = request.args.get("start_time")
    start_time = datetime.strptime(start_time, DATE_FORMAT)
    end_time = request.args.get("end_time")
    end_time = datetime.strptime(end_time, DATE_FORMAT)
    event = Event(
        name=name,
        location=location,
        start_time=start_time,
        end_time=end_time,
    )
    try:
        db.session.add(event)
        db.session.commit()
    except SQLAlchemyError as e:
        return handle_error(e)
    return handle_ok({"id": event.id})

@bp.route("/add_user")
def add_user():
    email = request.args.get("email")
    user = User(email=email)
    try:
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError as e:
        return handle_error(e)
    return handle_ok({"user_id": user.user_id})

@bp.route("/sign_event")
def sign_event():
    uid = request.args.get("user_id")
    id = request.args.get("id")
    e2u = Event2User(id=id, user_id=uid)
    try:
        result = db.session.query(User, Event).filter(
            User.user_id == uid,
            Event.id == id,
        )
        if result is None:
            return handle_error_str("Both the event and user should exist")
        db.session.add(e2u)
        db.session.commit()
    except SQLAlchemyError as e:
        return handle_error(e)
    return handle_ok()

@bp.route("/unsign_event")
def unsign_event():
    email = request.args.get("email")
    id = request.args.get("id")
    if id is None or email is None:
        return handle_error_str("should provide both email end event id")
    try:
        e2u = db.session.query(Event2User).filter(
            Event2User.user_id == User.user_id,
            User.email == email,
        ).first()
        if e2u is not None:
            db.session.delete(e2u)
            db.session.commit()
    except SQLAlchemyError as e:
        return handle_error(e)
    return handle_ok()

@bp.route("/get_user")
def get_user():
    email = request.args.get("email")
    if email is not None:
        user = db.session.query(User).filter(
            User.email == email,
        ).first()
        if user is None:
            return handle_error_str("No such user")
        eids = [eid[0] for eid in db.session.query(Event2User.id).filter(
            Event2User.user_id == user.user_id,
        )]
        return handle_ok({"user": user.serialize(), "events": eids})
    uid = request.args.get("user_id")
    if uid is not None:
        user = db.session.query(User).filter(
            User.user_id == uid,
        ).first()
        if user is None:
            return handle_error_str("No such user")
        eids = [eid[0] for eid in db.session.query(Event2User.id).filter(
            Event2User.user_id == uid,
        )]
        return handle_ok({"user": user.serialize(), "event": eids})
    return handle_error_str("No limitation")

@bp.route("/get_event")
def get_event():
    id = request.args.get("id")
    event = db.session.query(Event).filter(Event.id == id).first()
    if event is None:
        return handle_error_str("No such event")
    emails = [email[0] for email in db.session.query(User.email).filter(
        Event2User.id == id,
        User.user_id == Event2User.user_id,
    )]
    return handle_ok({"event": event.serialize(), "users":emails})



