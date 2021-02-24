#!/bin/bash

if [ -z $1 ]; then
  echo "Please define environment (dev / prod)"
  exit 1
fi

source etc/common.$1.env
source etc/server.$1.env
source etc/secrets.env

if [ "$1" == "dev" ] || [ "$1" == "demo" ]; then
  pipenv sync --dev
  pipenv run printenv
  pipenv run flask run -h $SERVER_HOST -p $SERVER_PORT
elif [ "$1" == "prod" ]; then
  pipenv sync
  pipenv run gunicorn \
    --workers 2 \
    --umask 0117 \
    --error-logfile - \
    --capture-output \
    --log-level=INFO \
    --pid $RESOURCE_PATH/argus_server.pid \
    --bind unix:$RESOURCE_PATH/argus_server.sock \
    --threads=2 \
    --timeout=400 \
    server:app
fi
