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

docker volume create pgdata-$1
docker run -d -it \
    --name argus-$1 \
    -p 127.0.0.1:5432:5432 \
    -v pgdata:/var/lib/postgresql/data \
    -e POSTGRES_USER=$DB_USER \
    -e POSTGRES_PASSWORD=$DB_PASSWORD \
    -e POSTGRES_DB=$DB_SCHEMA \
    postgres
