#!/bin/bash

if [ -z $1 ]; then
  echo "Please define environment (dev / prod)"
  exit 1
fi

source etc/common.$1.env
source etc/server.$1.env
source etc/secrets.env

source scripts/install.sh

. ./$PYENV/bin/activate

if [ "$1" == "dev" ] || [ "$1" == "demo" ]; then
  printenv
  $PYENV/bin/python3 -s -m flask run -h $SERVER_HOST -p $SERVER_PORT
elif [ "$1" == "prod" ]; then
  PYTHONUNBUFFERED=1 gunicorn \
    --workers 2 \
    --umask 0117 \
    --error-logfile - \
    --capture-output \
    --pid $RESOURCE_PATH/argus_server.pid \
    --bind unix:$RESOURCE_PATH/argus_server.sock \
    server:app
fi