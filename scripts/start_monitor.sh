#!/bin/bash

if [ -z $1 ]; then
  echo "Please define environment (dev / prod)"
  exit 1
fi

source etc/common.$1.env
source etc/monitor.$1.env
source etc/secrets.env

source scripts/install.sh

. ./$PYENV/bin/activate


if [ "$1" == "dev" ]; then
  # create file with path and set permissions
  install -Dv /dev/null $MONITOR_INPUT_SOCKET
  chown -R $USER:$USER $MONITOR_INPUT_SOCKET
  PYTHONPATH=src $PYENV/bin/python3 -s -m monitoring.__main__
elif [ "$1" == "prod" ]; then
  # create file with path and set permissions
  install -Dv /dev/null $MONITOR_INPUT_SOCKET
  chown -R argus:argus $MONITOR_INPUT_SOCKET
  printenv
  PYTHONPATH=src $PYENV/bin/python3 -u -s -m monitoring.__main__
fi
