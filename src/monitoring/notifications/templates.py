'''
Created on 2018. jan. 6.

@author: gkovacs
'''

ALERT_STARTED_SMS = 'Alert({id}) started at {time}!'
ALERT_STARTED_EMAIL = '''
Hi,

You have an alert({id}) at {source} since {time}.
The alert started on sensor(s): {sensors}!

argus security
'''

ALERT_STOPPED_SMS = 'Alert({id}) stopped at {time}!'
ALERT_STOPPED_EMAIL = '''
Hi,

The alert({id}) at {source} stopped at {time}!

argus security
'''