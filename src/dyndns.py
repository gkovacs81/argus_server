#!/usr/bin/env python

import json
import requests
import socket
from ipaddress import ip_address
from _socket import gaierror

from noipy.main import execute_update

from models import Option


def update_ip(force=False):
    '''
    Compare IP address in DNS server and actual lookup result.
    Update the IP address at DNSprovider if it's necesarry.
    :param force: force the update
    '''
    noip_config = Option.query.filter_by(name='network', section='dyndns').first()
    if noip_config:
        noip_config = json.loads(noip_config.value)
    print("Update dynamics DNS provider with options: %s" % noip_config)

    # DNS lookup IP from hostname
    try:
        current_ip = socket.gethostbyname(noip_config['hostname'])
    except gaierror:
        return False

    # Getting public IP
    new_ip = requests.get("https://ipconfig.co/ip").text.strip()
    try:
        new_ip = ip_address(new_ip)
    except ValueError:
        print("Invalid IP address: %s" % new_ip)
        return False

    print("IP: '%s' => '%s'" % (current_ip, new_ip))

    if new_ip != current_ip or force:
        noip_config['ip'] = new_ip
        result = save_ip(noip_config)
        print("Update result: '%s'" % result)
        return True
    else:
        print("No IP change")

    return True


def save_ip(noip_config):
    '''
    Save IP to the DNS provider
    :param noip_config: dictonary of settings (provider, username, passowrd, hostname, ip)
    '''
    class Arguments():
        pass

    args = Arguments()
    args.store = False
    args.provider = noip_config['provider']
    args.usertoken = noip_config['username']
    args.password = noip_config['password']
    args.hostname = noip_config['hostname']
    args.ip = noip_config['ip']
    return execute_update(args)


if __name__ == '__main__':
    update_ip()
