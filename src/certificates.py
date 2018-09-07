#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2018. ápr. 16.

@author: gkovacs
'''

import json
import subprocess

from pydbus import SystemBus
from os import symlink
from pathlib import Path, PosixPath

from models import Option


def generate_certificate():
    '''
    Generate certbot certificates with dynamic dsn provider
    '''
    print("Generating certbot certificate")
    noip_config = Option.query.filter_by(name='network', section='dyndns').first()
    if noip_config:
        noip_config = json.loads(noip_config.value)
    print("Generate certificate with options: %s" % noip_config)

    # non interactive
    subprocess.call([
        '/home/argus/certbot-auto',
         'certonly',
         '--webroot',
         '-w', '/home/argus/server/webapplication',
         '--agree-tos',
         '--email', noip_config['username'],
         "-d %s" % noip_config['hostname']
    ])


def swith2certbot():
    '''
    Changes the symlink for nginx using the certbot certificates instead of the self-signed
    '''
    print("Switch nginx to use certbot certificates...")
    Path('/usr/local/nginx/conf/snippets/certificates.conf').unlink()
    symlink('/usr/local/nginx/conf/snippets/certbot-signed.conf', '/usr/local/nginx/conf/snippets/certificates.conf')


def restart_nginx():
    '''
    Restarts the nginx-1.12.2 service with DBUS
    '''
    print("Restarting NGINX...")
    bus = SystemBus()
    systemd = bus.get('.systemd1')
    systemd.RestartUnit('nginx.service', 'fail')


def update_certificates():
    full_certificate = Path('/etc/letsencrypt/live/argus113.ddns.net/fullchain.pem')
    if not full_certificate.is_file():
        print("No certbot certificate found")
        generate_certificate()

    if full_certificate.is_file():
        if Path('/usr/local/nginx/conf/snippets/certificates.conf').resolve() == PosixPath('/usr/local/nginx/conf/snippets/self-signed.conf'):
            print("NGINX uses self-signed certificates")
            swith2certbot()
            restart_nginx()
        elif Path('/usr/local/nginx/conf/snippets/certificates.conf').resolve() == PosixPath('/usr/local/nginx/conf/snippets/certbot-signed.conf'):
            print("Using certbot certificates")
        else:
            print("Error detecting certificate configuration")
            return
    else:
        print("No certbot certificate found")


if __name__ == '__main__':
    update_certificates()

