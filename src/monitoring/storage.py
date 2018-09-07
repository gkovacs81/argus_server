'''
Created on 2017. dec. 3.

In memory storage for communicating between threads

@author: gkovacs
'''

# TODO: make it thread safe???

_data = dict()

def get(key):
    return _data[key]

def set(key, value):
    _data[key] = value
