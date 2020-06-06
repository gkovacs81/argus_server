
import os
import os.path
import re

from datetime import datetime as dt
from subprocess import check_output, CalledProcessError, run


def gettime_ntp(addr='0.pool.ntp.org'):
    # http://code.activestate.com/recipes/117211-simple-very-sntp-client/
    import socket
    import struct
    try:
        TIME1970 = 2208988800
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = ('\x1b' + 47 * '\0').encode('utf-8')
        client.sendto(data, (addr, 123))
        data, address = client.recvfrom(1024)
        if data:
            t = struct.unpack('!12I', data)[10]
            t -= TIME1970
            return dt.fromtimestamp(t).isoformat(sep=' ')
    except socket.gaierror:
        pass


def gettime_hw():
    try:
        result = re.search(
            "RTC time: [a-zA-Z]{0,4} ([0-9\\-: ]*)",
            check_output('timedatectl').decode('utf-8')
        )
        if result:
            return result.group(0)
    except CalledProcessError:
        pass


def get_timezone():
    full_path = os.readlink('/etc/localtime')
    return full_path.replace('/usr/share/zoneinfo/', '')


def sync_clock():
    network = gettime_ntp()

    if network is not None:
        # print("Network: {}".format(network))
        run(["date", "--set={}".format(network)])
        run(['/sbin/hwclock', '-w'])
    else:
        hw = gettime_hw()
        # print("HW: {}".format(hw))
        if hw is not None:
            run(["date", "--set={}".format(hw)])


def set_clock(settings):
    if 'timezone' in settings and os.path.isfile('/usr/share/zoneinfo/' + settings['timezone']):
        os.remove('/etc/localtime')
        os.symlink('/usr/share/zoneinfo/' + settings['timezone'], '/etc/localtime')
    if 'datetime' in settings and settings['datetime']:
        run(["date", "--set={}".format(settings['datetime'])])


if __name__ == '__main__':
    exit(sync_clock())
