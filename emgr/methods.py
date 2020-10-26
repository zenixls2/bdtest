from emgr.model import db, Serializer, Event, User, Event2User
from flask import Blueprint, request, jsonify, send_from_directory
from flask import g
from flask_mail import Mail, Message
from flask_restx import Api, Resource
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import os


DATE_FORMAT = "%Y/%m/%d-%H:%M:%S"

STATIC_FOLDER = os.path.join(os.pardir, "static")
mail = Mail()
bp = Blueprint("methods", __name__, static_folder=STATIC_FOLDER)
api = Api(bp, version="1.0",
    title="Event Management API",
    description="Simple Event Management API",
    doc='/doc/'
)


def handle_error(e):
    error = str(e.__dict__.get('orig') or 'error orig unknown')
    return jsonify({"status": "Error", "msg": error})

def handle_error_str(e):
    return jsonify({"status": "Error", "msg": e})

def handle_ok(content=None):
    content = content or {}
    return jsonify({"status": "Ok", **content})

@api.route("/")
class Index(Resource):
    def get(self):
        return api.send_static_file("index.html")

@api.route("/js/<path:path>")
class SendJs(Resource):
    def get(self, path):
        return send_from_directory("js", path)


@api.route("/listall")
class ListAll(Resource):
    def get(self):
        return jsonify(Serializer.serialize_list(Event.query.all()))

@api.route("/add_event")
@api.doc(params={
    'name': 'Event name',
    'location': 'Event location',
    'start_time': format('Start Time, in %s' % DATE_FORMAT),
    'end_time': format('End Time, in %s' % DATE_FORMAT)
})
class AddEvent(Resource):
    def get(self):
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
        except Exception as e:
            return handle_error_str(str(e))
        return handle_ok({"id": event.id})

@api.route("/add_user")
@api.doc(params={'email': "Email address"})
class AddUser(Resource):
    def get(self):
        email = request.args.get("email")
        user = User(email=email)
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError as e:
            return handle_error(e)
        except Exception as e:
            return handle_error_str(str(e))
        return handle_ok({"user_id": user.user_id})

@api.route("/sign_event")
@api.doc(params={
    'user_id': 'user_id, User primary key',
    'id': 'id, Event primary key',
    'send_mail': 'bool, send notification mail on success, default to False'
})
class SignEvent(Resource):
    def get(self):
        uid = request.args.get("user_id")
        id = request.args.get("id")
        send_mail = request.args.get("send_mail") or False
        e2u = Event2User(id=id, user_id=uid)
        try:
            result = db.session.query(User, Event).filter(
                User.user_id == uid,
                Event.id == id,
            ).first()
            if result is None:
                return handle_error_str("Both the event and user should exist")
            db.session.add(e2u)
            db.session.commit()
            print(result)
            if send_mail:
                msg = Message("Notice", recipients=[result[0].email])
                msg.html = format("sign to event id=%d", id)
                mail.send(msg)
        except SQLAlchemyError as e:
            return handle_error(e)
        except Exception as e:
            return handle_error_str(str(e))
        return handle_ok()

@api.route("/unsign_event")
@api.doc(params={
    'email': 'email address to remove from event',
    'id': 'id, Eent primary key',
})
class UnsignEvent(Resource):
    def get(self):
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
        except Exception as e:
            return handle_error_str(str(e))
        return handle_ok()

@api.route("/get_user")
@api.doc(params={
    'email': 'By email, optional (at least one param need to be exist)',
    'user_id': 'By user_id (User primary key), optional (at least one param need to be exist)',
})
class GetUser(Resource):
    def get(self):
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

@api.route("/get_event")
@api.doc(params={'id': 'by Event primary key'})
class GetEvent(Resource):
    def get(self):
        id = request.args.get("id")
        event = db.session.query(Event).filter(Event.id == id).first()
        if event is None:
            return handle_error_str("No such event")
        emails = [email[0] for email in db.session.query(User.email).filter(
            Event2User.id == id,
            User.user_id == Event2User.user_id,
        )]
        return handle_ok({"event": event.serialize(), "users":emails})



