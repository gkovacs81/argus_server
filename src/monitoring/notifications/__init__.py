from monitoring.notifications.notifier import ALERT_STARTED, ALERT_STOPPED
from monitoring.notifications.queue import NotificationQueue


def notify_alert_started(alert_id, sensors, time):
    queue = NotificationQueue.get_queue()
    queue.put({
        'type': ALERT_STARTED,
        'id': alert_id,
        'source': "argus113",
        'sensors': sensors,
        'time': time,
    })


def notify_alert_stopped(alert_id, time):
    queue = NotificationQueue.get_queue()
    queue.put({
        'type': ALERT_STOPPED,
        'id': alert_id,
        'source': "argus113",
        'time': time
    })
