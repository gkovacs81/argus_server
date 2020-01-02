#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

try:
    from models import *
except KeyError:
    pass
from server import db

from sqlalchemy.exc import ProgrammingError

from monitoring.constants import ROLE_ADMIN, ROLE_USER


def cleanup():
    print("Clean up database...")
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print(" - Clear table %s" % table)
        try:
            db.session.execute(table.delete())
            db.session.commit()
        except ProgrammingError:
            db.session.rollback()
    print("Database is empty")


def env_prod():
    db.session.add(User(name="Administrator", role=ROLE_ADMIN, access_code="1234"))
    print(" - Created admin user")
    db.session.add_all([
        SensorType(1, name='Motion', description='Detect motion'),
        SensorType(2, name='Tamper', description='Detect sabotage'),
        SensorType(3, name='Open', description='Detect opening'),
        SensorType(4, name='Break', description='Detect glass break')
    ])
    print(" - Created sensor types")

    kt1 = KeypadType(1, 'DSC', 'DSC keybus (DSC PC-1555RKZ)')
    db.session.add_all([kt1])
    print(" - Created keypad types")

    db.session.commit()


def env_dev():
    db.session.add_all([
        User(name="Administrator", role=ROLE_ADMIN, access_code="1234"),
        User(name="Teszt Elek", role=ROLE_USER, access_code="1111")
    ])

    for alert in Alert.query.all():
        alert.sensors = []
    db.session.commit()

    z1 = Zone(name="Azonnali", description="Azonnali riasztás")
    z2 = Zone(name="Távozó késleltetett", away_delay=20, description="Távozáskor/érkezésekor késletetett")
    z3 = Zone(name="Maradó", description="Maradó élesítés esetén nem riaszt")
    z4 = Zone(name="Maradó késleltetett", stay_delay=20, description="Maradó élesítés esetén késleltetve riaszt")
    z5 = Zone(name="Távozó/maradó késleltetett", away_delay=20, stay_delay=20, description="Távozó és maradó élesytés esetén késleltetve riaszt")
    db.session.add_all([z1, z2, z3, z4, z5])

    st1 = SensorType(1, 'Motion', 'Motion sensor')
    st2 = SensorType(2, 'Tamper', 'Tamper sensor')
    st3 = SensorType(3, 'Open', 'Door open sensor')
    st4 = SensorType(4, 'Break', 'Break sensor')
    db.session.add_all([st1, st2, st3, st4])

    s1 = Sensor(channel=0, sensor_type=st1, zone=z2, description="Garázs bejárati ajtó feletti mozgésérzékelő")
    s2 = Sensor(channel=1, sensor_type=st1, zone=z5, description="Előszoba mozgésérzékelő")
    s3 = Sensor(channel=2, sensor_type=st1, zone=z4, description="Étkező/konyha mozgésérzékelő")
    s4 = Sensor(channel=3, sensor_type=st1, zone=z1, description="Nappali mozgésérzékelő")
    s5 = Sensor(channel=4, sensor_type=st1, zone=z3, description="Gyerekszoba mozgésérzékelő")
    s6 = Sensor(channel=5, sensor_type=st1, zone=z3, description="Hálószoba mozgésérzékelő")
    s7 = Sensor(channel=6, sensor_type=st4, zone=z1, description="Tamper kör")
    db.session.add_all([s1, s2, s3, s4, s5, s6, s7])

    kt1 = KeypadType(1, 'DSC', 'DSC keybus (DSC PC-1555RKZ)')
    db.session.add_all([kt1])
    print(" - Created keypad types")

    k1 = Keypad(keypad_type=kt1)
    db.session.add_all([k1])
    print(" - Created keypads")

    db.session.commit()


def main():
    environments = []
    for attribute, value in globals().items():
        if attribute.startswith('env_'):
            environments.append(attribute.replace('env_', ''))

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--create", action='store_true', help="Re-create database content")
    parser.add_argument("-d", "--delete", action='store_true', help="Delete database content")
    parser.add_argument(dest="environment", help="/".join(environments), metavar="environment")
    args = parser.parse_args()

    if args.delete:
        cleanup()

    if args.create:
        create_method = globals()['env_' + args.environment]
        print("Creating '%s' environment..." % args.environment)
        create_method()
        print("Environment create")


if __name__ == '__main__':
    main()
