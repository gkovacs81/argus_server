# -*- coding: utf-8 -*-
# @Author: Gábor Kovács
# @Date:   2021-02-25 20:10:13
# @Last Modified by:   Gábor Kovács
# @Last Modified time: 2021-02-25 20:10:18


class KeypadBase:
    def __init__(self, clock_pin, data_pin):
        self._clock = clock_pin
        self._data = data_pin
        self.pressed = None
        self.enabled = True

    def initialise(self):
        pass

    def set_error(self, state: bool):
        pass

    def set_ready(self, state: bool):
        pass

    def set_armed(self, state: bool):
        pass

    def invalid_code(self):
        pass
