#!/bin/bash

if [ -z $1 ]; then
  echo "Please define environment (dev / prod)"
  exit 1
fi

source etc/common.$1.env
source etc/monitor.$1.env
source etc/secrets.env

if [ "$1" == "dev" ]; then
  pipenv sync --dev
  pipenv run printenv
  # create file with path and set permissions
  install -Dv /dev/null $MONITOR_INPUT_SOCKET
  chown -R $USER:$USER $MONITOR_INPUT_SOCKET
  pipenv run python -d -s -m monitoring
elif [ "$1" == "prod" ]; then
  # update the system clock from RTC
  /sbin/hwclock --hctosys >> /var/log/hwclock.log
  # create file with path and set permissions
  install -Dv /dev/null $MONITOR_INPUT_SOCKET
  chown -R argus:argus $MONITOR_INPUT_SOCKET
  pipenv run python -u -s -m monitoring
fi
