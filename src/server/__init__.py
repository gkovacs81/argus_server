import functools
import logging
import os
import re
from datetime import datetime as dt
from os.path import isfile, join

import jose.exceptions
from click import Option
from flask import Flask, abort, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from jose import jwt

from monitoring.constants import ROLE_USER
from server.ipc import IPCClient
from server.version import __version__
from tools.clock import get_timezone, gettime_hw, gettime_ntp

argus_application_folder = os.path.join(
    os.getcwd(), os.environ.get("SERVER_STATIC_FOLDER", "")
)

# app = Flask(__name__, static_folder=argus_application_folder, static_url_path='/')
app = Flask(__name__)
# app.logger.debug("App folder: %s", argus_application_folder)

POSTGRES = {
    "user": os.environ.get("DB_USER", None),
    "pw": os.environ.get("DB_PASSWORD", None),
    "db": os.environ.get("DB_SCHEMA", None),
    "host": os.environ.get("DB_HOST", None),
    "port": os.environ.get("DB_PORT", None),
}
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s" % POSTGRES
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.use_reloader = False

# avoid reloading records from database after session commit
db = SQLAlchemy(app, session_options={"expire_on_commit": False})

from models import *


@app.route("/")
def root():
    app.logger.debug("ROOT: return index.html")
    return send_from_directory(argus_application_folder, "index.html")


def authenticated(check_permissions=True):
    def _authenticated(request_handler):
        @functools.wraps(request_handler)
        def check_access(*args, **kws):
            auth_header = request.headers.get("Authorization")
            # app.logger.info("Header: %s", auth_header)
            token = auth_header.split(" ")[1] if auth_header else ""
            if token:
                # app.logger.info("Token: %s", token)
                try:
                    data = jwt.decode(
                        token, os.environ.get("SECRET"), algorithms="HS256"
                    )
                    if (
                        check_permissions
                        and "role" in data
                        and data["role"] == ROLE_USER
                        and request.method != "GET"
                    ):
                        app.logger.info(
                            "Operation %s not permitted for user='%s/%s' from %s",
                            request,
                            data["name"],
                            data["role"],
                            request.remote_addr,
                        )
                        return jsonify({"error": "operation not permitted"}), 403
                    return request_handler(*args, **kws)
                except jose.exceptions.JWTError:
                    app.logger.info(
                        "Bad token (%s) from %s", token, request.remote_addr
                    )
                    return jsonify({"error": "operation not permitted"}), 403
            else:
                app.logger.info(
                    "Request without authentication info from %s", request.remote_addr
                )
                return jsonify({"error": "operation not permitted"}), 403

        return check_access

    return _authenticated


@app.route("/api/authenticate", methods=["GET", "POST"])
def authenticate():
    # app.logger.debug("Authenticating...")
    # check user credentials and return fake jwt token if valid
    remote_address = (
        request.remote_addr
        if request.remote_addr != "b''"
        else request.headers.get("X-Real-Ip")
    )
    # app.logger.debug("Input from '%s': '%s'", remote_address, request.json)
    for user in User.query.all():
        if user.access_code == hash_access_code(request.json["access_code"]):
            return jsonify(
                {
                    "user_token": jwt.encode(
                        {"name": user.name, "role": user.role},
                        os.environ.get("SECRET"),
                        algorithm="HS256",
                    ),
                    "device_token": jwt.encode(
                        {"ip": remote_address},
                        os.environ.get("SECRET"),
                        algorithm="HS256",
                    ),
                }
            )

    return jsonify(False)


@app.route("/api/alerts", methods=["GET"])
@authenticated()
def get_alerts():
    # app.logger.debug("Request: %s", request.args.get('alerting'))
    return jsonify([i.serialize for i in Alert.query.order_by(Alert.start_time.desc())])


@app.route("/api/alert", methods=["GET"])
@authenticated()
def get_alert():
    alert = (
        Alert.query.filter_by(end_time=None).order_by(Alert.start_time.desc()).first()
    )
    if alert:
        return jsonify(alert.serialize)
    else:
        return jsonify(None)


@app.route("/api/users", methods=["GET", "POST"])
@authenticated()
def users():
    if request.method == "GET":
        return jsonify([i.serialize for i in User.query.all()])
    elif request.method == "POST":
        data = request.json
        user = User(
            name=data["name"], role=data["role"], access_code=data["access_code"]
        )
        db.session.add(user)
        db.session.commit()
        return jsonify(user.serialize)


@app.route("/api/user/<int:user_id>", methods=["GET", "PUT", "DELETE"])
@authenticated()
def user(user_id):
    if request.method == "GET":
        user = User.query.get(user_id)
        if user:
            return jsonify(user.serialize)
        abort(404)
    elif request.method == "PUT":
        user = User.query.get(user_id)
        if user.update(request.json):
            db.session.commit()
        return jsonify(True)
    elif request.method == "DELETE":
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify(True)

    return jsonify({"error": "unknonw action"})


@app.route("/api/sensors/", methods=["GET", "POST"])
@authenticated()
def sensors():
    if request.method == "GET":
        # app.logger.debug("Request: %s", request.args.get('alerting'))
        if not request.args.get("alerting"):
            return jsonify(
                [
                    i.serialize
                    for i in Sensor.query.filter_by(deleted=False).order_by(
                        Sensor.channel.asc()
                    )
                ]
            )
        return jsonify([i.serialize for i in Sensor.query.filter_by(alert=True).all()])
    elif request.method == "POST":
        data = request.json
        zone = Zone.query.get(request.json["zone_id"])
        sensor_type = SensorType.query.get(data["type_id"])
        sensor = Sensor(
            channel=data["channel"],
            zone=zone,
            sensor_type=sensor_type,
            description=data["description"],
        )
        db.session.add(sensor)
        db.session.commit()
        ipc_client = IPCClient()
        ipc_client.update_configuration()
        return jsonify(sensor.serialize)


@app.route("/api/sensors/reset-references", methods=["PUT"])
@authenticated()
def sensors_reset_references():
    if request.method == "PUT":
        for sensor in Sensor.query.all():
            sensor.reference_value = None

        db.session.commit()
        ipc_client = IPCClient()
        return jsonify(ipc_client.update_configuration())


@app.route("/api/sensor/<int:sensor_id>", methods=["GET", "PUT", "DELETE"])
@authenticated()
def sensor(sensor_id):
    if request.method == "GET":
        sensor = Sensor.query.filter_by(id=sensor_id, deleted=False).first()
        if sensor:
            return jsonify(sensor.serialize)
        abort(404)
    elif request.method == "DELETE":
        sensor = Sensor.query.get(sensor_id)
        sensor.deleted = True
        db.session.commit()
        ipc_client = IPCClient()
        ipc_client.update_configuration()
        return jsonify(True)
    elif request.method == "PUT":
        sensor = Sensor.query.get(sensor_id)
        if sensor.update(request.json):
            db.session.commit()
            ipc_client = IPCClient()
            ipc_client.update_configuration()
        return jsonify(True)

    return jsonify({"error": "unknonw action"})


@app.route("/api/sensortypes")
@authenticated()
def sensortypes():
    # app.logger.debug("Request: %s", request.args.get('alerting'))
    return jsonify([i.serialize for i in SensorType.query.all()])


@app.route("/api/sensor/alert", methods=["GET"])
@authenticated()
def get_sensor_alert():
    if request.args.get("sensor_id"):
        return jsonify(
            Sensor.query.filter_by(id=request.args.get("sensor_id"), alert=True).first()
            is not None
        )
    else:
        return jsonify(Sensor.query.filter_by(alert=True).first() is not None)


@app.route("/api/zones/", methods=["GET", "POST"])
@authenticated()
def zones():
    if request.method == "GET":
        return jsonify([i.serialize for i in Zone.query.filter_by(deleted=False).all()])
    elif request.method == "POST":
        zone = Zone()
        zone.update(request.json)
        if not zone.description:
            zone.description = zone.name
        db.session.add(zone)
        db.session.commit()
        ipc_client = IPCClient()
        ipc_client.update_configuration()
        return jsonify(zone.serialize)

    return jsonify({"error": "unknown action"})


@app.route("/api/zone/<int:zone_id>", methods=["GET", "PUT", "DELETE"])
@authenticated()
def zone(zone_id):
    if request.method == "GET":
        return jsonify(Zone.query.get(zone_id).serialize)
    elif request.method == "DELETE":
        zone = Zone.query.get(zone_id)
        zone.deleted = True
        db.session.commit()
        ipc_client = IPCClient()
        ipc_client.update_configuration()
        return jsonify(True)
    elif request.method == "PUT":
        zone = Zone.query.get(zone_id)
        if zone.update(request.json):
            ipc_client = IPCClient()
            ipc_client.update_configuration()
        db.session.commit()
        return jsonify(zone.serialize)


@app.route("/api/monitoring/arm", methods=["GET"])
@authenticated()
def get_arm():
    ipc_client = IPCClient()
    return jsonify(ipc_client.get_arm())


@app.route("/api/monitoring/arm", methods=["PUT"])
@authenticated(check_permissions=False)
def put_arm():
    ipc_client = IPCClient()
    return jsonify(ipc_client.arm(request.args.get("type")))


@app.route("/api/monitoring/disarm", methods=["PUT"])
@authenticated(check_permissions=False)
def disarm():
    return jsonify(IPCClient().disarm())


@app.route("/api/monitoring/state", methods=["GET"])
@authenticated()
def get_state():
    ipc_client = IPCClient()
    return jsonify(ipc_client.get_state())


@app.route("/api/config/<string:option>/<string:section>", methods=["GET", "PUT"])
@authenticated()
def option(option, section):
    if request.method == "GET":
        db_option = Option.query.filter_by(name=option, section=section).first()
        return jsonify(db_option.serialize) if db_option else jsonify(None)
    elif request.method == "PUT":
        db_option = Option.query.filter_by(name=option, section=section).first()
        if db_option is None:
            db_option = Option(name=option, section=section, value="")
            db.session.add(db_option)

        changed = db_option.update_value(request.json)
        db.session.commit()

        if option == "notifications":
            if changed:
                ipc_client = IPCClient()
                ipc_client.update_configuration()
        elif db_option.name == "network" and db_option.section == "dyndns":
            if os.environ.get("ARGUS_DEVELOPMENT", "0") == "0":
                ipc_client = IPCClient()
                ipc_client.update_dyndns()

        return jsonify(True)


@app.route("/api/version", methods=["GET"])
def version():
    return __version__


@app.route("/api/clock", methods=["GET"])
@authenticated()
def get_clock():
    result = {
        "system": dt.now().isoformat(sep=" ")[:19],
        "hw": gettime_hw(),
        "timezone": get_timezone(),
    }

    network = gettime_ntp()
    if network:
        result["network"] = network
    else:
        result["network"] = None

    return jsonify(result)


@app.route("/api/clock", methods=["PUT"])
def set_clock():
    ipc_client = IPCClient()
    ipc_client.set_clock(request.json)

    return jsonify(True)


@app.route("/api/clock/sync", methods=["PUT"])
def sync_clock():
    ipc_client = IPCClient()
    ipc_client.sync_clock()

    return jsonify(True)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    # app.logger.debug("Working in: %s", os.environ.get('SERVER_STATIC_FOLDER', ''))
    # app.logger.debug("FALLBACK for path: %s", path)

    # check compression
    compress = os.environ["COMPRESS"].lower() == "true"
    if compress and (path.endswith(".js") or path.endswith(".css")):
        # app.logger.debug("Use compression")
        path += ".gz"
    else:
        compress = False

    # detect language from url path (en|hu)
    languages = os.environ["LANGUAGES"].split(" ")
    result = re.search("(" + "|".join(languages) + ")", path)
    language = result.group(0) if result else ""

    # app.logger.debug("Language: %s from %s", language if language else "No language in URL", languages)
    if language == "en":
        path = path.replace("en/", "")

    # app.logger.debug("FALLBACK for path processed: %s", path)

    # return with file if exists
    # app.logger.debug("Checking for %s", path)
    if isfile(join(argus_application_folder, path)):
        # app.logger.debug("Path exists without language: %s", path)
        response = send_from_directory(argus_application_folder, path)
        if compress:
            response.headers["Content-Encoding"] = "gzip"
        return response
    elif language and isfile(join(argus_application_folder, language, "index.html")):
        # app.logger.debug("Path exists with language: %s",join(language, 'index.html'))
        return send_from_directory(
            join(argus_application_folder, language), "index.html"
        )

    # or return with the index file
    # app.logger.debug("INDEX without language: %s", join(language, 'index.html'))
    return send_from_directory(argus_application_folder, "index.html")


if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
