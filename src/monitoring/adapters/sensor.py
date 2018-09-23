'''
Created on 2017. aug. 28.

@author: gkovacs
'''

import os
import logging
from monitoring.constants import LOG_ADSENSOR

if os.uname()[4][:3] == 'arm':
    from gpiozero import MCP3008
else:
    #from monitoring.adapters.mock import TimeBasedMockMCP3008 as MCP3008
    from monitoring.adapters.mock.MCP3008 import PatternBasedMockMCP3008 as MCP3008

CLK = 21
MISO = 20
MOSI = 16
CS = [12, 1]

# number of channels on MCP3008
CHANNEL_COUNT=8

# total number of channels on the board
IO_NUMBER = int(os.environ["INPUT_NUMBER"])


class SensorAdapter(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._channels = []
        self._logger = logging.getLogger(LOG_ADSENSOR)

        for i in range(IO_NUMBER):
            self._logger.debug("Channel ({:2}-{:2} on BCM{:0>2}) creating...".format(i+1, i%CHANNEL_COUNT+1, CS[i//CHANNEL_COUNT]))
            self._channels.append(MCP3008(channel=i%CHANNEL_COUNT, clock_pin=CLK, mosi_pin=MOSI, miso_pin=MISO, select_pin=CS[i//CHANNEL_COUNT]))

    def get_value(self, channel):
        if 0 < channel < 15:
            # channel numbering correction board numbering CH1..CH15 => array 0..14
            return self._channels[channel-1].value
        else:
            return 0

    def get_values(self):
        values = []
        for channel in self._channels:
            values.append(channel.value)
        return values

    @property
    def channel_count(self):
        return IO_NUMBER
