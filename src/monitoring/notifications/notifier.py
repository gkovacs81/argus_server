import json
import logging
import os
import smtplib

from queue import Empty
from smtplib import SMTPException
from threading import Thread

from monitoring.notifications.templates import *
from monitoring.notifications.queue import NotificationQueue
from monitoring.constants import LOG_NOTIFIER, THREAD_NOTIFIER
from models import Option

if os.uname()[4][:3] == 'arm':
    from monitoring.adapters.gsm import GSM
else:
    from monitoring.adapters.mock.gsm import GSM


'''
Messages

{
    "type": "alert_started" / "alert_stopped",
    "id": "alert id", 
    "source": "address",
    "sensors": ["Sensor name"],
    "time": "start time",
}


'''

ALERT_STARTED = "alert_started"
ALERT_STOPPED = "alert_stopped"

'''
options = {
    "subscriptions": {
        "sms": {
            ALERT_STARTED: True,
            ALERT_STOPPED: True,
            WEEKLY_REPORT: False
        },
        "email": {
            ALERT_STARTED: False,
            ALERT_STOPPED: False,
            WEEKLY_REPORT: False
        }
    },
    "email": {
        'smtp_username': 'smtp_username',
        'smtp_password': 'smtp_password',
        'email_address': 'email_address'
    },
    "gsm": {
        "phone_number": "phone number"
    }
}
'''



class Notifier(Thread):

    def __init__(self, stop_event):
        super(Notifier, self).__init__(name=THREAD_NOTIFIER)
        self._queue = NotificationQueue.get_queue()
        self._stop_event = stop_event
        self._options = self.getOptions('Notifier')
        self._logger = logging.getLogger(LOG_NOTIFIER)
        self._gsm = GSM()

    def run(self):
        self._logger.info("Notifier started...")
        self._gsm.setup()
        while not self._stop_event.is_set():
            try:
                message = self._queue.get(timeout=1)
                if not self.sendMessage(message):
                    self._queue.put(message)
            except Empty:
                pass
        self._logger.info("Notifier stopped...")

    def getOptions(self, section):
        options = {}
        for section_name in ('email', 'gsm', 'subscription'):
            section = Option.query.filter_by(name='notifications', section=section_name).first()
            options[section_name] = json.loads(section.value) if section else ''
        return options

    def sendMessage(self, message):
        self._logger.info("New message: %s", message)
        success = False
        has_subscription = False
        try:
            if self._options["subscriptions"]['sms'][message['type']]:
                if message['type'] == ALERT_STARTED:
                    has_subscription = True
                    success |= self.notify_alert_started_SMS(message)
                elif message['type'] == ALERT_STOPPED:
                    has_subscription = True
                    success |= self.notify_alert_stopped_SMS(message)
    
            if self._options["subscriptions"]['email'][message['type']]:
                if message['type'] == ALERT_STARTED:
                    has_subscription = True
                    success |= self.notify_alert_started_email(message)
                elif message['type'] == ALERT_STOPPED:
                    has_subscription = True
                    success |= self.notify_alert_stopped_email(message)
        except KeyError:
            self._logger.info("No subscription configured!")
            pass

        return not (not success and has_subscription)

    def notify_alert_started_SMS(self, message):
        return self.notify_SMS(ALERT_STARTED_SMS.format(**message))

    def notify_alert_stopped_SMS(self, message):
        return self.notify_SMS(ALERT_STOPPED_SMS.format(**message))

    def notify_alert_started_email(self, message):
        return self.notify_email("Alert started", ALERT_STARTED_EMAIL.format(**message))

    def notify_alert_stopped_email(self, message):
        return self.notify_email("Alert stopped", ALERT_STOPPED_EMAIL.format(**message))

    def notify_SMS(self, message):
        return self._gsm.sendSMS(self._options['gsm']['phone_number'], message)

    def notify_email(self, subject, content):
        self._logger.info("Sending email ...")
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login(self._options['email']['smtp_username'], self._options['email']['smtp_password'])

            message = 'Subject: {}\n\n{}'.format(subject, content).encode(encoding='utf_8', errors='strict')
            server.sendmail(from_addr='info@argus', to_addrs=self._options['email']['email_address'], msg=message)
            server.quit()
        except SMTPException as error:
            self._logger.error("Can't send email %s ", error)
            return False

        self._logger.info("Sent email")
        return True

