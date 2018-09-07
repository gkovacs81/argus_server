'''
Created on 2018. jan. 8.

@author: gkovacs
'''

import json
import logging
import os

from models import Option
from monitoring.constants import LOG_ADGSM


class GSM(object):

    def __init__(self):
        self._logger = logging.getLogger(LOG_ADGSM)
        self._options = None

    def setup(self):
        self._options = {}
        self._options['pin_code'] = '4321'
        self._options['port'] = os.environ['GSM_PORT']
        self._options['baud'] = os.environ['GSM_PORT_BAUD']

        self._logger.info('Connecting to GSM modem on %s with %s baud (PIN: %s)...', 
                          self._options['port'],
                          self._options['baud'],
                          self._options['pin_code'])

    def destroy(self):
        pass

    def sendSMS(self, phone_number, message):
        self._logger.info('Message sent to %s: "%s"', phone_number, message)
        return True
