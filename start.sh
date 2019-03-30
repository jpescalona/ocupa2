#!/bin/bash

docker-compose build
docker-compose up -d
docker-compose exec uwsgi ./manage.py migrate --noinput
docker-compose exec uwsgi ./manage.py collectstatic --noinput
docker-compose exec uwsgi ./manage.py install_labels 
