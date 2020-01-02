#!/bin/bash

if [ -z $1 ]; then
  echo "Please define environment (dev / prod)"
  exit 1
fi

source etc/common.$1.env
source etc/monitor.$1.env
source etc/secrets.env

if [ "$1" == "dev" ]; then
  kill -s TERM $(cat $MONITOR_PID_FILE)
elif [ "$1" == "prod" ]; then
  kill -s TERM $(cat $MONITOR_PID_FILE)
  sleep 10s
  if kill -s 0 $(cat $MONITOR_PID_FILE); then
    kill -s KILL $(cat $MONITOR_PID_FILE) || true
  fi
fi
