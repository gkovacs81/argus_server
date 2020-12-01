"""
Created on 2017. szept. 7.

@author: gkovacs
"""
import json
import logging
import socket
from os import chmod, chown, environ, makedirs, path, remove
from threading import Thread

from monitoring import storage
from monitoring.constants import (LOG_IPC, MONITOR_ARM_AWAY, MONITOR_ARM_STAY,
                                  MONITOR_DISARM, MONITOR_SET_CLOCK,
                                  MONITOR_SYNC_CLOCK, MONITOR_UPDATE_CONFIG,
                                  MONITOR_UPDATE_SECURE_CONNECTION, MONITOR_UPDATE_KEYPAD,
                                  THREAD_IPC)
from tools.clock import set_clock, sync_clock
from tools.connection import SecureConnection

MONITOR_INPUT_SOCKET = environ["MONITOR_INPUT_SOCKET"]


class IPCServer(Thread):
    """
    Class for handling the actions from the server and executing them on monitoring.
    """

    def __init__(self, stop_event, broadcaster):
        """
        Constructor
        """
        super(IPCServer, self).__init__(name=THREAD_IPC)
        self._logger = logging.getLogger(LOG_IPC)
        self._stop_event = stop_event
        self._broadcaster = broadcaster
        self._initialize_socket()
        self._logger.info("IPC server created")

    def _initialize_socket(self):
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket.settimeout(1.0)

        try:
            remove(MONITOR_INPUT_SOCKET)
        except OSError:
            pass

        self.create_socket_file()
        self._socket.bind(MONITOR_INPUT_SOCKET)
        self._socket.listen(1)

        try:
            chmod(MONITOR_INPUT_SOCKET, int(environ["PERMISSIONS"], 8))
            chown(MONITOR_INPUT_SOCKET, int(environ["USER_ID"]), int(environ["GROUP_ID"]))
            self._logger.info("Socket permissions fixed")
        except KeyError:
            self._logger.info("No permission or owner defined")

    def create_socket_file(self):
        filename = MONITOR_INPUT_SOCKET
        if not path.exists(path.dirname(filename)):
            self._logger.info("Create socket file: %s", MONITOR_INPUT_SOCKET)
            makedirs(path.dirname(filename))

    def handle_actions(self, message):
        if message["action"] == MONITOR_ARM_AWAY:
            self._logger.info("Action: arm AWAY")
            self._broadcaster.send_message(MONITOR_ARM_AWAY)
        if message["action"] == MONITOR_ARM_STAY:
            self._logger.info("Action: arm STAY")
            self._broadcaster.send_message(MONITOR_ARM_STAY)
        elif message["action"] == MONITOR_DISARM:
            self._logger.info("Action: disarm")
            self._broadcaster.send_message(MONITOR_DISARM)
        elif message["action"] == "get_arm":
            arm = storage.get("arm")
            return {"type": arm}
        elif message["action"] == "get_state":
            return {"state": storage.get("state")}
        elif message["action"] == MONITOR_UPDATE_CONFIG:
            self._logger.info("Update configuration...")
            self._broadcaster.send_message(MONITOR_UPDATE_CONFIG)
        elif message["action"] == MONITOR_UPDATE_KEYPAD:
            self._logger.info("Update keypad...")
            self._broadcaster.send_message(MONITOR_UPDATE_KEYPAD)
        elif message["action"] == MONITOR_UPDATE_SECURE_CONNECTION:
            self._logger.info("Update secure connection...")
            SecureConnection(self._stop_event).run()
        elif message["action"] == MONITOR_SYNC_CLOCK:
            sync_clock()
        elif message["action"] == MONITOR_SET_CLOCK:
            del message["action"]
            set_clock(message)

        return {"result": True}

    def run(self):
        self._logger.info("IPC server started")
        # read all the messages
        while not self._stop_event.is_set():
            connection = None
            try:
                connection, _ = self._socket.accept()
            except socket.timeout:
                pass

            # read all the parts of a messages
            while connection:
                data = connection.recv(1024)

                if not data:
                    break

                self._logger.debug("Received action: '%s'", data)

                response = self.handle_actions(json.loads(data.decode()))

                try:
                    connection.send(json.dumps(response).encode())
                except BrokenPipeError:
                    pass

            if connection:
                connection.close()

        self._logger.info("IPC server stopped")
