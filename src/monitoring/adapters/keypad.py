import logging
import os
from queue import Empty
from threading import Thread

from monitoring.adapters.mock.keypad import KeypadBase, MockKeypad
from monitoring.constants import (LOG_ADKEYPAD, MONITOR_DISARM, MONITOR_STOP,
                                  MONITOR_UPDATE_KEYPAD, THREAD_KEYPAD)

if os.uname()[4][:3] == "arm":
    from monitoring.adapters.keypads.dsc import DSCKeypad

COMMUNICATION_PERIOD = 0.5  # sec


class Keypad(Thread):
    # DSC COMMANDS
    KEYBUS_QUERY = 0x4C
    PARTITION_STATUS = 0x05
    ZONE_STATUS = 0x27
    ZONE_LIGHTS = 0x0A
    DATETIME_STATUS = 0xA5
    BEEP = 0x64

    # pins
    CLOCK_PIN = 5
    DATA_PIN = 0

    def __init__(self, commands, responses):
        super(Keypad, self).__init__(name=THREAD_KEYPAD)
        self._logger = logging.getLogger(LOG_ADKEYPAD)
        self._commands = commands
        self._responses = responses
        self._codes = []
        self._keypad: KeypadBase = None

    def set_type(self, type):
        # check if running on Raspberry
        if os.uname()[4][:3] != "arm":
            self._keypad = MockKeypad(Keypad.CLOCK_PIN, Keypad.DATA_PIN)
        elif type == "dsc":
            with self._commands.mutex:
                self._commands.queue.clear()
            self._keypad = DSCKeypad(Keypad.CLOCK_PIN, Keypad.DATA_PIN)
        elif type is None:
            self._logger.debug("Keypad removed")
            self._keypad = None
        else:
            self._logger.error("Unknown keypad type: %s", type)
        self._logger.debug("Keypad created type: %s", type)

    def run(self):
        # load from db
        self.set_type("dsc")
        self._codes = ["1234", "1111"]

        try:
            self.communicate()
        except KeyboardInterrupt:
            self._logger.error("Keyboard interrupt")
            pass
        except Exception:
            self._logger.exception("Keypad communication failed!")

        self._logger.info("Keypad manager stopped")

    def communicate(self):
        self._keypad.initialise()

        buttons = ""
        while True:
            try:
                # self._logger.debug("Wait for command...")
                message = self._commands.get(timeout=COMMUNICATION_PERIOD)
                self._logger.info("Command: %s", message)

                if message == MONITOR_UPDATE_KEYPAD:
                    # load keypad from db
                    pass
                elif message == MONITOR_DISARM:
                    self._keypad.set_armed(False)
                elif message == MONITOR_STOP:
                    break

            except Empty:
                pass

            self._keypad.communicate()

            pressed = self._keypad.keypresses[-1] if self._keypad.keypresses else None
            if pressed and pressed != " ":
                self._logger.debug("Pressed: %s", pressed)
            if pressed in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
                buttons += pressed

            if buttons in self._codes:
                self._logger.info("Code: %s", buttons)
                self._responses.put(MONITOR_DISARM)
                self._keypad.set_armed(False)
                self._logger.info("Disarmed")
                buttons = ""
            elif len(buttons) == 4:
                self._logger.info("Invalid code")
                buttons = ""
