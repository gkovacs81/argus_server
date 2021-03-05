#!/bin/bash

if [ -z $1 ]; then
  echo "Please define environment (dev / prod)"
  exit 1
fi

source etc/common.$1.env
source etc/server.$1.env
source etc/secrets.env

pipenv run src/manage.py db init
pipenv run src/manage.py db migrate
pipenv run src/manage.py db upgrade
