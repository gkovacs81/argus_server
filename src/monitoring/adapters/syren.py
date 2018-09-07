'''
Created on 2017. aug. 28.

@author: gkovacs
'''

import logging
import os

from monitoring.constants import LOG_ADSYREN

if os.uname()[4][:3] == 'arm':
    from gpiozero.output_devices import DigitalOutputDevice
else:
    from monitoring.adapters.mock.output import Output as DigitalOutputDevice


class SyrenAdapter(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._channels = []
        self._logger = logging.getLogger(LOG_ADSYREN)
        self._is_alerting = False
        self._output = DigitalOutputDevice(pin=23)


    def alert(self, start=True):
        if start:
            self._logger.info("Syren on")
            self._is_alerting = True
            self._output.on()
        else:
            self._logger.info("Syren off")
            self._is_alerting = False
            self._output.off()


    @property
    def is_alerting(self):
        return self._is_alerting

