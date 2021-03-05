# -*- coding: utf-8 -*-
# @Author: Gábor Kovács
# @Date:   2021-02-25 20:06:58
# @Last Modified by:   Gábor Kovács
# @Last Modified time: 2021-02-25 20:07:17
# @Description: In memory storage for communicating between threads
# TODO: make it thread safe???

_data = dict()

ARM_STATE = 0
MONITORING_STATE = 1
POWER_STATE = 2


def get(key):
    return _data.get(key, None)


def set(key, value):
    _data[key] = value
