'''
Created on 2017. szept. 13.

@author: gkovacs
'''

import logging
import pytz

from threading import Thread, BoundedSemaphore

from models import *
from monitoring.adapters.syren import SyrenAdapter
from monitoring.socket_io import send_syren_state, send_alert_state,\
    send_system_state_change
from monitoring.constants import ARM_AWAY, ARM_STAY, ARM_DISARM,\
    MONITORING_SABOTAGE, LOG_ALERT, THREAD_ALERT
from multiprocessing import Queue
from queue import Empty 
from monitoring import storage
from monitoring.notifications.notifier import Notifier


SYREN_DEFAULT_ALERT_TIME = 5
SYREN_DEFAULT_SUSPEND_TIME = 5

class SensorAlert(Thread):
    '''
    classdocs
    '''
    _syren_alert = None
    _sensor_queue = Queue()

    def __init__(self, sensor_id, arm_type, stop_event):
        '''
        Constructor
        '''
        super(SensorAlert, self).__init__(name=THREAD_ALERT)
        self._sensor_id = sensor_id
        self._arm_type = arm_type
        self._stop_event = stop_event
        self._logger = logging.getLogger(LOG_ALERT)



    def run(self):
        sensor = Sensor.query.get(self._sensor_id)
        if self._arm_type == ARM_AWAY:
            delay = sensor.zone.away_delay
        elif self._arm_type == ARM_STAY:
            delay = sensor.zone.stay_delay
        elif self._arm_type == ARM_DISARM:
            delay = sensor.zone.disarmed_delay
        else:
            self._logger.error('Unknown arm type = %s!', self._arm_type)

        self._logger.info('Alert started on channel(%s) waiting %s sec before starting syren', sensor.channel, delay)
        if not self._stop_event.wait(delay):
            self._logger.info('Start syren because not disarmed in %s secs', delay)
            SyrenAlert.start_syren(self._arm_type, SensorAlert._sensor_queue, self._stop_event)
            SensorAlert._sensor_queue.put(self._sensor_id)
            if self._arm_type == ARM_DISARM:
                storage.set('state', MONITORING_SABOTAGE)
                send_system_state_change(MONITORING_SABOTAGE)
        else:
            self._logger.info('Sensor alert stopped')


class SyrenAlert(Thread):

    _semaphore = BoundedSemaphore()
    _alert = None

    @classmethod
    def start_syren(cls, arm_type, sensor_queue, stop_event):
        with cls._semaphore:
            if not cls._alert:
                cls._alert = SyrenAlert(arm_type, sensor_queue, stop_event)
                cls._alert.start()
            return cls._alert
    
    @classmethod
    def get_sensor_queue(cls):
        return cls._sensor_queue

    def __init__(self, arm_type, sensor_queue, stop_event):
        super(SyrenAlert, self).__init__(name=THREAD_ALERT)
        self._arm_type = arm_type
        self._sensor_queue = sensor_queue
        self._stop_event = stop_event
        self._logger = logging.getLogger(LOG_ALERT)
        self._syren = SyrenAdapter()
        self._alert = None


    def run(self):
        self.start_alert()
        while not self._stop_event.is_set():
            self._syren.alert(True)
            send_syren_state(True)
            self._logger.info("Syren started")
            if self._stop_event.wait(SYREN_DEFAULT_ALERT_TIME):
                break

            self.handle_sensors()

            self._syren.alert(False)
            send_syren_state(False)
            self._logger.info("Syren suspended")
            if self._stop_event.wait(SYREN_DEFAULT_SUSPEND_TIME):
                break

            self.handle_sensors()

        self.stop_alert()
        self._logger.info("Syren stopped")

    def start_alert(self):
        start_time = datetime.datetime.now(pytz.timezone('CET'))
        self._alert = Alert(self._arm_type, start_time=start_time, sensors=[])
        db.session.add(self._alert)
        if not self.handle_sensors():
            db.session.commit()

        send_alert_state(json.dumps(self._alert.serialize))
        Notifier.notify_alert_started(self._alert.id, list(map(lambda alert_sensor: alert_sensor.sensor.description, self._alert.sensors)), start_time)

    def stop_alert(self):
        with SyrenAlert._semaphore:
            SyrenAlert._alert = None
            self.handle_sensors()
            self._syren.alert(False)
            self._alert.end_time = datetime.datetime.now(pytz.timezone('CET'))
            db.session.commit()

            send_alert_state(json.dumps(False))
            send_syren_state(None)
            Notifier.notify_alert_stopped(self._alert.id, self._alert.end_time)

    def handle_sensors(self):
        sensor_added = False
        try:
            while True:
                sensor_id = self._sensor_queue.get(False)
                sensor = Sensor.query.get(sensor_id)

                # check if already added to the alert
                already_added = False
                for alert_sensor in self._alert.sensors:
                    if alert_sensor.sensor.id == sensor_id:
                        already_added = True

                if not already_added:
                    alert_sensor = AlertSensor(channel=sensor.channel, description=sensor.description)
                    alert_sensor.sensor = sensor
                    self._alert.sensors.append(alert_sensor)
                    sensor_added = True
                    self._logger.debug("Added sensor by id: %s", sensor_id)
                else:
                    self._logger.debug("Sensor by id: %s already added", sensor_id)
        except Empty:
            pass

        if sensor_added:
            db.session.commit()

        return sensor_added


