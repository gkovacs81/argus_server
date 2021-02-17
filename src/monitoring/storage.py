'''
Created on 2017. dec. 3.

In memory storage for communicating between threads

@author: gkovacs
'''

# TODO: make it thread safe???

_data = dict()

ARM_STATE = 0
MONITORING_STATE = 1
POWER_STATE = 2

def get(key):
    return _data.get(key, None)

def set(key, value):
    _data[key] = value
