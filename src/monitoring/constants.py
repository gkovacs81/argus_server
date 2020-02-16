'''
Created on 2017. dec. 3.

@author: gkovacs
'''
from logging import DEBUG, INFO

# Threads and logging
THREAD_SERVICE  = 'Service'
THREAD_MONITOR  = 'Monitor'
THREAD_IPC      = 'IPC'
THREAD_NOTIFIER = 'Notifier'
THREAD_SOCKETIO = 'SocketIO'
THREAD_ALERT    = 'Alert'
THREAD_KEYPAD   = 'Keypad'

LOG_SERVICE   = THREAD_SERVICE
LOG_MONITOR   = THREAD_MONITOR
LOG_IPC       = THREAD_IPC
LOG_ALERT     = THREAD_ALERT
LOG_SOCKETIO  = THREAD_SOCKETIO
LOG_NOTIFIER  = THREAD_NOTIFIER
LOG_ADSENSOR  = 'AD.Sensor'
LOG_ADPOWER   = 'AD.Power'
LOG_ADSYREN   = 'AD.Syren'
LOG_ADGSM     = 'AD.GSM'
LOG_ADKEYPAD  = 'AD.Keypad'

LOGGING_MODULES = [
    (LOG_SERVICE, INFO),
    (LOG_MONITOR, DEBUG),
    (LOG_IPC, INFO),
    (LOG_ALERT, INFO),
    (LOG_SOCKETIO, DEBUG),
    (LOG_NOTIFIER, INFO),
    (LOG_ADSENSOR, INFO),
    (LOG_ADSYREN, INFO),
    (LOG_ADGSM, INFO),
    (LOG_ADKEYPAD, INFO)
]

# INTERNAL CONSTANTS
# monitoring system commands
MONITOR_ARM_AWAY = 'monitor_arm_away'
MONITOR_ARM_STAY = 'monitor_arm_stay'
MONITOR_DISARM = 'monitor_disarm'
MONITOR_UPDATE_CONFIG = 'monitor_update_config'
MONITOR_UPDATE_KEYPAD = 'monitor_update_keypad'
MONITOR_UPDATE_DYNDNS = 'monitor_update_dyndns'
MONITOR_STOP = 'monitor_stop'
MONITOR_SYNC_CLOCK = 'monitor_sync_clock'
MONITOR_SET_CLOCK = 'monitor_set_clock'

'''---------------------------------------------------------------'''
# CONSTANTS USED ALSO BY THE WEB APPLICATION
# arm types
ARM_AWAY = 'arm_away'
ARM_STAY = 'arm_stay'
ARM_DISARM = 'disarm'

# alert types
ALERT_AWAY = 'alert_away'
ALERT_STAY = 'alert_stay'
ALERT_SABOTAGE = 'alert_sabotage'

# monitoring system states
MONITORING_STARTUP = 'monitoring_startup'
MONITORING_READY = 'monitoring_ready'
MONITORING_UPDATING_CONFIG = 'monitoring_updating_config'
MONITORING_INVALID_CONFIG = 'monitoring_invalid_config'
MONITORING_ARMED = 'monitoring_armed'
MONITORING_SABOTAGE = 'monitoring_sabotage'
MONITORING_ERROR = 'monitoring_error'

ROLE_ADMIN = 'admin'
ROLE_USER = 'user'
