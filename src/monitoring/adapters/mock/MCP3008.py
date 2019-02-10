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
            if self._starttime and self._starttime + TimeBasedMockMCP3008.CHANGE_TIME > time():
                return 1
            else:
                self._starttime = None

            if int(time()) % 10 == 0:
                self._starttime = time()
                return 1

        return TimeBasedMockMCP3008.DEFAULT_VALUE


class PatternBasedMockMCP3008(object):

    def __init__(self, channel=None, clock_pin=None, mosi_pin=None, miso_pin=None, select_pin=None):
        self._channel = channel
        self._logger = logging.getLogger(LOG_ADSENSOR)
        self._starttime = None
        self._alert_source = []
        # clock
        self.i = 0

    @property
    def value(self):
        try:
            # print("Values: %s / %s" % (self._alert_source, self._channel))
            value = self._alert_source[self.i][self._channel]
        except (KeyError, TypeError, IndexError):
            value = 0
            self._logger.warn("No value for channel=%s on clock=%s in %s!", self._channel, self.i, self.__class__)

        # step clock
        self.i += 1
        if self. i == len(self._alert_source):
            self.i = 0

        return value


class ShortAlertMCP3008(PatternBasedMockMCP3008):

    SHORT_ALERT = [
        [0],
        [0],
        [0],
        [0],
        [0],
        [0],
        [0],
        [0],
        [0],
        [0],

        [1],
        [1],
        [1],
        [1],
        [1],
        [1],
        [1],
        [1],
        [1],
        [1],

        [0],
        [0],
        [0],
        [0],
        [0],
        [0],
        [0],
        [0],
        [0],
        [0]
    ]

    def __init__(self, *args, **kwargs):
        super(ShortAlertMCP3008, self).__init__(*args, **kwargs)
        self._alert_source = ShortAlertMCP3008.SHORT_ALERT


class DoubleAlertMCP3008(PatternBasedMockMCP3008):

    DOUBLE_ALERT = [
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

    def __init__(self, *args, **kwargs):
        super(DoubleAlertMCP3008, self).__init__(*args, **kwargs)
        self._alert_source = DoubleAlertMCP3008.DOUBLE_ALERT


class PowerMCP3008(PatternBasedMockMCP3008):

    POWER_ALERT = [
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    def __init__(self, *args, **kwargs):
        super(PowerMCP3008, self).__init__(*args, **kwargs)
        self._alert_source = PowerMCP3008.POWER_ALERT
