import logging
import os
import sys

from queue import Queue
from signal import SIGTERM, signal
from threading import Thread, Event

from monitoring.constants import MONITOR_STOP, LOGGING_MODULES, THREAD_SOCKETIO,\
    LOG_SERVICE
from monitoring.ipc import IPCServer
from monitoring.monitor import Monitor
from monitoring.notifications.notifier import Notifier
from monitoring.socket_io import start_socketio
from time import sleep


def initialize_logging():
    for module in LOGGING_MODULES:
        logger = logging.getLogger(module)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('monitoring.log')
        formatter = logging.Formatter('%(asctime)s-[%(threadName)10s] %(levelname)5s %(name)9s: %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logging.getLogger('SocketIOServer').setLevel(logging.INFO)

def createPidFile():
    pid = str(os.getpid())
    f = open(os.environ['MONITOR_PID_FILE'], 'w')
    f.write(pid+"\n")
    f.close()


def start():
    createPidFile()
    initialize_logging()

    logger = logging.getLogger(LOG_SERVICE)

    stop_event = Event()
    actions = Queue()

    monitor = Monitor(actions)
    monitor.start()

    ipc_server = IPCServer(stop_event, actions) 
    ipc_server.start()

    notifier = Notifier(stop_event)
    notifier.daemon = True
    notifier.start()

    # start the socket IO server in he main thread
    socketio_server = Thread(target=start_socketio, name=THREAD_SOCKETIO, daemon=True)
    socketio_server.start()

    def stop_service():
        logger.info("Stopping service...")
        stop_event.set()
        actions.put(MONITOR_STOP)
        monitor.join()
        logger.debug("Monitor thread stopped")
        ipc_server.join()
        logger.debug("IPC thread stopped")
        logger.info("All threads stopped")
        sys.exit(0)

    def signal_term_handler(signal, frame):
        logger.debug('Received signal (SIGTERM)')
        stop_service()

    signal(SIGTERM, signal_term_handler)

    '''
    The main thread checks the health of the sub threads and crashes the application if any problem happens.
    If the application stops the service running system has to restart it clearly.

    May be later threads can be implemented safe to avoid restarting the application.
    '''
    while True:
        try:
            for thread in (monitor, ipc_server, notifier, socketio_server):
                if not thread.is_alive():
                    logger.error("Thread crashed: %s", thread.name)
                    stop_service()
            sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interruption!!!")
            break

    stop_service()

if __name__ == '__main__':
    start()
