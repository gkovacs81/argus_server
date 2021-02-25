# -*- coding: utf-8 -*-
# @Author: Gábor Kovács
# @Date:   2021-02-25 20:05:48
# @Last Modified by:   Gábor Kovács
# @Last Modified time: 2021-02-25 20:05:48
class Broadcaster(object):
    """Send message to registered queues."""

    def __init__(self, queues):
        self._queues = queues

    def add_queue(self, queue):
        """Register queues to broadcast messages"""
        self._queues.append(queue)

    def send_message(self, message):
        """Broadcast message"""
        for queue in self._queues:
            queue.put(message)
