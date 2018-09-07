'''
Created on 2018. ápr. 4.

@author: gkovacs
'''

from crontab import CronTab


def enable_dyndns_job(enable=True):
    argus_cron = CronTab(user='argus')
    jobs = list(argus_cron.find_command('argus_dyndns'))
    job = jobs[0] if len(jobs) > 0 else None 
    if job is None:
        job = argus_cron.new(
            command="systemd-cat -t 'argus_dyndns'  bash -c '. /home/argus/server/pyenv/bin/activate; source /home/argus/server/etc/common.prod.env ;python /home/argus/server/src/dyndns.py'",
            comment='Update the IP address at the dynamic DNS provider')
        job.every().minutes()
    job.enable(enable)
    argus_cron.write()


def enable_certbot_job(enable=True):
    argus_cron = CronTab(user='root')
    jobs = list(argus_cron.find_command('argus_certbot'))
    job = jobs[0] if len(jobs) > 0 else None
    if job is None:
        job = argus_cron.new(
            command="systemd-cat -t 'argus_certbot' bash -c '. /home/argus/server/pyenv/bin/activate; source /home/argus/server/etc/common.prod.env; /home/argus/server/pyenv/bin/python /home/argus/server/src/certificates.py'",
            comment='Generate or update certificate with certbot')
        job.every().day()
    job.enable(enable)
    argus_cron.write()

