
class KeypadBase:

    def __init__(self, clock_pin, data_pin):
        self._clock = clock_pin
        self._data = data_pin
        self.pressed = None

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
