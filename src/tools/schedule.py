'''
Created on 2018. ápr. 4.

@author: gkovacs
'''
import logging

from crontab import CronTab

from monitoring.constants import LOG_IPC


def enable_dyndns_job(enable=True):
    try:
        argus_cron = CronTab(user='argus')
    except OSError as error:
        logging.getLogger(LOG_IPC).error("Can't access crontab! %s", error)
        return

    jobs = list(argus_cron.find_command('argus_dyndns'))
    job = jobs[0] if len(jobs) > 0 else None
    if job is None:
        job = argus_cron.new(
            command="systemd-cat -t 'argus_dyndns'  bash -c '. /home/argus/server/pyenv/bin/activate; source /home/argus/server/etc/server.prod.env; source /home/argus/server/etc/secrets.env; python /home/argus/server/src/dyndns.py'",
            comment='Update the IP address at the dynamic DNS provider')
        job.hours.every(1)
    job.enable(enable)
    argus_cron.write()


def enable_certbot_job(enable=True):
    try:
        root_cron = CronTab(user='root')
    except OSError as error:
        logging.getLogger(LOG_IPC).error("Can't access crontab! %s", error)
        return

    jobs = list(root_cron.find_command('argus_certbot'))
    job = jobs[0] if len(jobs) > 0 else None
    if job is None:
        job = root_cron.new(
            command="systemd-cat -t 'argus_certbot' bash -c '. /home/argus/server/pyenv/bin/activate; source /home/argus/server/etc/server.prod.env; source /home/argus/server/etc/secrets.env; /home/argus/server/pyenv/bin/python /home/argus/server/src/certbot.py'",
            comment='Generate or update certificate with certbot')
        job.day.every(1)
    job.enable(enable)
    root_cron.write()
