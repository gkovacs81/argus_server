#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

try:
    from models import *
except KeyError:
    pass
from server import db

from monitoring.constants import ROLE_ADMIN, ROLE_USER


def cleanup():
    print("Clean up database...")
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print(" - Clear table %s" % table)
        db.session.execute(table.delete())
        db.session.commit()
    print("Database is empty")


def env_prod():
    db.session.add(User(name="Administrator", role=ROLE_ADMIN, access_code="1234"))
    print(" - Created admin user")
    db.session.add_all([
        SensorType(name='Motion sensor', description='Detect motion'),
        SensorType(name='Break sensor', description='Detect glass break'),
        SensorType(name='Tamper', description='Detect sabotage')
    ])
    print(" - Created sensor types")
    db.session.commit()


def env_dev():
    db.session.add(User(name="Administrator", role=ROLE_ADMIN, access_code="1234"))
    print(" - Created admin user")
    db.session.add_all([
        SensorType(name='Motion sensor', description='Detect motion'),
        SensorType(name='Break sensor', description='Detect glass break'),
        SensorType(name='Tamper', description='Detect sabotage')
    ])
    print(" - Created sensor types")
    db.session.commit()


def env_test():
    db.session.add_all([
        User(name="Administrator", role=ROLE_ADMIN, access_code="1234"),
        User(name="Teszt Elek", role=ROLE_USER, access_code="1111")
    ])

    for alert in Alert.query.all():
        alert.sensors = []
    db.session.commit()

    Sensor.query.delete()
    SensorType.query.delete()
    Zone.query.delete()
    Alert.query.delete()

    z1 = Zone(name="Azonnali", away_delay=0, stay=False, stay_delay=0, description="Azonnali risztás")
    z2 = Zone(name="Távozó késleltetett", away_delay=20, stay=False, stay_delay=0, description="Távozáskor/érkezésekor késletetett")
    z3 = Zone(name="Maradó", away_delay=0, stay=True, stay_delay=0, description="Maradó élesítés esetén nem riaszt")
    z4 = Zone(name="Maradó késleltetett", away_delay=0, stay=True, stay_delay=20, description="Maradó élesítés esetén késleltetve riaszt")
    z5 = Zone(name="Távozó/maradó késleltetett", away_delay=20, stay=True, stay_delay=20, description="Távozó és maradó élesytés esetén késleltetve riaszt")
    db.session.add_all([z1, z2, z3, z4, z5])

    st1 = SensorType('Motion', 'Motion sensor')
    st2 = SensorType('Tamper', 'Tamper sensor')
    st3 = SensorType('Break', 'Break sensor')
    st4 = SensorType('Open', 'Door open sensor')
    db.session.add_all([st1, st2, st3, st4])

    s1 = Sensor(channel=0, zone=z2, sensor_type=st1, description="Garázs bejárati ajtó feletti mozgésérzékelő")
    s2 = Sensor(channel=1, zone=z5, sensor_type=st1, description="Előszoba mozgésérzékelő")
    s3 = Sensor(channel=2, zone=z4, sensor_type=st1, description="Étkező/konyha mozgésérzékelő")
    s4 = Sensor(channel=3, zone=z1, sensor_type=st1, description="Nappali mozgésérzékelő")
    s5 = Sensor(channel=4, zone=z3, sensor_type=st1, description="Gyerekszoba mozgésérzékelő")
    s6 = Sensor(channel=5, zone=z3, sensor_type=st1, description="Hálószoba mozgésérzékelő")
    s7 = Sensor(channel=6, zone=z1, sensor_type=st1, description="Tamper kör")
    db.session.add_all([s1, s2, s3, s4, s5, s6, s7])

    db.session.commit()


def main():
    environments = []
    for attribute, value in globals().items():
        if attribute.startswith('env_'):
            environments.append(attribute.replace('env_', ''))

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cleanup", action='store_true', help="Delete all data before creating new records")
    parser.add_argument(dest="environment", help="/".join(environments), metavar="environment")
    args = parser.parse_args()

    if args.cleanup:
        cleanup()

    create_method = globals()['env_' + args.environment]
    print("Creating '%s' environment..." % args.environment)
    create_method()
    print("Environment create")


if __name__ == '__main__':
    main()
