'''
Created on 2017. szept. 13.

@author: gkovacs
'''

import json
import socket

from os import environ
from monitoring.constants import MONITOR_DISARM, MONITOR_UPDATE_CONFIG,\
    MONITOR_ARM_AWAY, ARM_STAY, MONITOR_ARM_STAY, ARM_AWAY,\
    MONITOR_UPDATE_DYNDNS, MONITOR_SYNC_CLOCK, MONITOR_SET_CLOCK


class IPCClient(object):
    '''
    classdocs
    '''
    _socket = None

    def __init__(self):
        if not self._socket:
            self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._socket.connect(environ['MONITOR_INPUT_SOCKET'])

    def disarm(self):
        return self._send_message({
            'action': MONITOR_DISARM
        })

    def get_arm(self):
        return self._send_message({
            'action':'get_arm'
        })

    def arm(self, arm_type):
        if arm_type == ARM_AWAY:
            return self._send_message({
                'action': MONITOR_ARM_AWAY
            })
        elif arm_type == ARM_STAY:
            return self._send_message({
                'action': MONITOR_ARM_STAY
            })
        else:
            print('Unknown arm type: %s' % arm_type)

    def get_state(self):
        return self._send_message({
            'action': 'get_state'
        })

    def update_configuration(self):
        return self._send_message({
            'action': MONITOR_UPDATE_CONFIG
        })
        
    def update_dyndns(self):
        return self._send_message({
            'action': MONITOR_UPDATE_DYNDNS
        })

    def sync_clock(self):
        return self._send_message({
            'action': MONITOR_SYNC_CLOCK
        })
        
    def set_clock(self, settings):
        message = {
            'action': MONITOR_SET_CLOCK
        }
        message = {**message, **settings}
        return self._send_message(message)

    def _send_message(self, message):
        self._socket.send(json.dumps(message).encode())
        data = self._socket.recv(1024)
        return json.loads(data.decode())
