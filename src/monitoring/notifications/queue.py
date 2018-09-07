'''
Created on 2018. jan. 6.

@author: gkovacs
'''

from queue import Queue

class NotificationQueue(Queue):
    '''Singleton queue for Notifier'''
    _queue = None

    @classmethod
    def get_queue(cls):
        if not cls._queue:
            cls._queue = Queue()
        return cls._queue