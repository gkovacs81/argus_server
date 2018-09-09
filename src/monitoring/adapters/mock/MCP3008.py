import os
import logging

from time import time
from monitoring.constants import LOG_ADSENSOR


class TimeBasedMockMCP3008(object):
    CHANGE_TIME = 11
    DEFAULT_VALUE = 0.1

    def __init__(self, channel=None, clock_pin=None, mosi_pin=None, miso_pin=None, select_pin=None):
        self._channel = channel
        self._logger = logging.getLogger(LOG_ADSENSOR)
        self._starttime = None

    @property
    def value(self):
        if self._channel == 0:
            if self._starttime and self._starttime + CHANGE_TIME > time():
                return 1
            else:
                self._starttime = None

            if int(time()) % 10 == 0:
                self._starttime = time()
                return 1

        return DEFAULT_VALUE

class PatternBasedMockMCP3008(object):

    double_alert = [
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        
        [1, 0],
        [1, 0],
        [1, 0],
        [1, 0],
        [1, 0],
        [1, 0],
        [1, 1],
        [1, 1],
        [1, 1],
        [1, 1],
        
        [1, 1],
        [1, 1],
        [0, 1],
        [0, 1],
        [0, 1],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0]
    ]

    short_alert = [
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        
        [1, 0],
        [1, 0],
        [1, 0],
        [1, 0],
        [1, 0],
        [1, 0],
        [1, 0],
        [1, 0],
        [1, 0],
        [1, 0],
        
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0]
    ]

    def __init__(self, channel=None, clock_pin=None, mosi_pin=None, miso_pin=None, select_pin=None):
        self._channel = channel
        self._logger = logging.getLogger(LOG_ADSENSOR)
        self._starttime = None
        self.i = 0

    @property
    def value(self):
        values = PatternBasedMockMCP3008.short_alert
        if len(values[self.i]) > self._channel:
            value = values[self.i][self._channel]
        else:
            value = 0
        self.i += 1
        if self. i == len(values):
            self.i = 0

        return value






