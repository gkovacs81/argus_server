import copy
import datetime
import hashlib
import json
import locale
import os
from copy import deepcopy

from sqlalchemy.orm.mapper import validates

from server import db


def hash_access_code(access_code):
    return hashlib.sha256((access_code + ":" + os.environ.get("SALT")).encode("utf-8")).hexdigest()


def update_record(record, attributes, data):
    """Update the given attributes of a record (dict) based on a dictionary"""
    record_changed = False
    for key, value in data.items():
        if key in attributes:
            if value != getattr(record, key, value):
                setattr(record, key, value)
                record_changed = True
    return record_changed


def merge_dicts(target, source):
    if not source:
        return
    if not target:
        target = source
        return

    for k, v in source.items():
        if type(v) == list:
            if k not in target:
                target[k] = copy.deepcopy(v)
            else:
                target[k].extend(v)
        elif type(v) == dict:
            if k not in target:
                target[k] = copy.deepcopy(v)
            else:
                merge_dicts(target[k], v)
        elif type(v) == set:
            if k not in target:
                target[k] = v.copy()
            else:
                target[k].update(v.copy())
        else:
            target[k] = copy.copy(v)


def filter_keys(data, keys):
    # filter key
    for filter_key in keys:
        if filter_key in data:
            del data[filter_key]

    # filter sub dictionaries
    for _, value in data.items():
        if type(value) == dict:
            filter_keys(value, keys)


class BaseModel(db.Model):
    """Base data model for all objects"""

    __abstract__ = True

    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        """Define a base way to print models"""
        return "%s(%s)" % (self.__class__.__name__, {column: value for column, value in self.__dict__.items()})

    def json(self):
        """
        Define a base way to jsonify models, dealing with datetime objects
        """
        return {column: value if not isinstance(value, datetime.date) else value.strftime("%Y-%m-%d") for column, value in self.__dict__.items()}


class SensorType(BaseModel):
    """Model for sensor type table"""

    __tablename__ = "sensor_type"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))
    description = db.Column(db.String)

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @property
    def serialize(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class Sensor(BaseModel):
    """Model for the sensor table"""

    __tablename__ = "sensor"

    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.Integer, nullable=False)
    reference_value = db.Column(db.Float)
    alert = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean, default=True)
    deleted = db.Column(db.Boolean, default=False)
    description = db.Column(db.String, nullable=False)

    zone_id = db.Column(db.Integer, db.ForeignKey("zone.id"), nullable=False)
    zone = db.relationship("Zone", backref=db.backref("zone", lazy="dynamic"))

    type_id = db.Column(db.Integer, db.ForeignKey("sensor_type.id"), nullable=False)
    type = db.relationship("SensorType", backref=db.backref("sensor_type", lazy="dynamic"))
    alerts = db.relationship("AlertSensor", back_populates="sensor")

    def __init__(self, channel, sensor_type, zone=None, description=None):
        self.channel = channel
        self.zone = zone
        self.type = sensor_type
        self.description = description
        self.enabled = True
        self.deleted = False

    def update(self, data):
        return update_record(self, ("channel", "enabled", "description", "zone_id", "type_id"), data)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "channel": self.channel,
            "alert": self.alert,
            "description": self.description,
            "zone_id": self.zone_id,
            "type_id": self.type_id,
            "enabled": self.enabled,
        }


class Alert(BaseModel):
    """Model for alert table"""

    __tablename__ = "alert"

    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String)
    start_time = db.Column(db.DateTime(timezone=True))
    end_time = db.Column(db.DateTime(timezone=True))
    sensors = db.relationship("AlertSensor", back_populates="alert")

    def __init__(self, alert_type, start_time, sensors, end_time=None):
        self.alert_type = alert_type
        self.start_time = start_time
        self.end_time = end_time
        self.sensors = sensors

    @property
    def serialize(self):
        locale.setlocale(locale.LC_ALL, "")
        return {
            "id": self.id,
            "alert_type": self.alert_type,
            "start_time": self.start_time.replace(microsecond=0, tzinfo=None).isoformat(sep=" "),
            "end_time": self.end_time.replace(microsecond=0, tzinfo=None).isoformat(sep=" ") if self.end_time else "",
            "sensors": [
                {"id": alert_sensor.sensor_id, "channel": alert_sensor.channel, "type_id": alert_sensor.type_id, "description": alert_sensor.description}
                for alert_sensor in self.sensors
            ],
        }


class AlertSensor(BaseModel):
    __tablename__ = "alert_sensor"
    alert_id = db.Column(db.Integer, db.ForeignKey("alert.id"), primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id"), primary_key=True)
    channel = db.Column(db.Integer)
    type_id = db.Column(db.Integer, db.ForeignKey("sensor_type.id"), nullable=False)
    description = db.Column(db.String)
    sensor = db.relationship("Sensor", back_populates="alerts")
    alert = db.relationship("Alert", back_populates="sensors")

    def __init__(self, channel, type_id, description):
        self.channel = channel
        self.type_id = type_id
        self.description = description


class Zone(BaseModel):
    """Model for zone table"""

    __tablename__ = "zone"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String(128), nullable=False)
    disarmed_delay = db.Column(db.Integer, default=None, nullable=True)
    away_delay = db.Column(db.Integer, default=None, nullable=True)
    stay_delay = db.Column(db.Integer, default=None, nullable=True)
    deleted = db.Column(db.Boolean, default=False)

    def __init__(self, name="zone", disarmed_delay=None, away_delay=0, stay_delay=0, description="Default zone"):
        self.name = name
        self.description = description
        self.disarmed_delay = disarmed_delay
        self.away_delay = away_delay
        self.stay_delay = stay_delay

    def update(self, data):
        return update_record(self, ("name", "description", "disarmed_delay", "away_delay", "stay_delay"), data)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "disarmed_delay": self.disarmed_delay,
            "away_delay": self.away_delay,
            "stay_delay": self.stay_delay,
        }

    @validates("disarmed_delay", "away_delay", "stay_delay")
    def validates_away_delay(self, key, delay):
        assert delay and delay >= 0 or not delay
        return delay


class User(BaseModel):
    """Model for role table"""

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(12), nullable=False)
    access_code = db.Column(db.String, nullable=False)
    fourkey_code = db.Column(db.String, nullable=False)
    comment = db.Column(db.String(256), nullable=True)

    def __init__(self, name, role, access_code, fourkey_code=None):
        self.name = name
        self.email = ""
        self.role = role
        self.access_code = hash_access_code(access_code)
        self.fourkey_code = hash_access_code(access_code[:4])

    def update(self, data):
        if "access_code" in data and data["access_code"]:
            data["access_code"] = hash_access_code(data["access_code"])
            if not data["fourkey_code"]:
                data["fourkey_code"] = hash_access_code(data["access_code"][:4])
            else:
                data["fourkey_code"] = hash_access_code(data["fourkey_code"])
            return update_record(self, ("name", "role", "access_code", "fourkey_code"), data)
        else:
            return update_record(self, ("name", "email", "role", "comment"), data)

    @property
    def serialize(self):
        return {"id": self.id, "name": self.name, "email": self.email, "role": self.role, "comment": self.comment}


class Option(BaseModel):
    """Model for option table"""

    __tablename__ = "option"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    section = db.Column(db.String(32), nullable=False)
    value = db.Column(db.String)

    def __init__(self, name, section, value):
        self.name = name
        self.section = section
        self.value = value

    def update_value(self, value):
        """Update the value field (merging dictionaries). Return true if value changed"""
        if not self.value:
            self.value = json.dumps(value)
            return True
        else:
            tmp_value = json.loads(self.value)
            merge_dicts(tmp_value, value)
            tmp_value = json.dumps(tmp_value)
            changed = self.value != tmp_value
            self.value = tmp_value
            return changed

    @property
    def serialize(self):
        filtered_value = deepcopy(json.loads(self.value))
        filter_keys(filtered_value, ["smtp_password"])
        filter_keys(filtered_value, ["password"])
        return {"name": self.name, "section": self.section, "value": json.dumps(filtered_value)}


class Keypad(BaseModel):
    """Model for keypad table"""

    __tablename__ = "keypad"

    id = db.Column(db.Integer, primary_key=True)
    enabled = db.Column(db.Boolean, default=True)

    type_id = db.Column(db.Integer, db.ForeignKey("keypad_type.id"), nullable=False)
    type = db.relationship("KeypadType", backref=db.backref("keypad_type", lazy="dynamic"))

    def __init__(self, keypad_type, enabled=True):
        self.type = keypad_type
        self.enabled = enabled

    def update(self, data):
        return update_record(self, ("enabled", "type_id"), data)

    @property
    def serialize(self):
        return {"id": self.id, "type_id": self.type_id, "enabled": self.enabled}


class KeypadType(BaseModel):
    """Model for keypad type table"""

    __tablename__ = "keypad_type"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    description = db.Column(db.String)

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @property
    def serialize(self):
        return {"id": self.id, "name": self.name, "description": self.description}
