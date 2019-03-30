#!/bin/bash

docker-compose build
docker-compose up -d
docker-compose exec uwsgi ./manage.py migrate --noinput
docker-compose exec uwsgi ./manage.py collectstatic --noinput
docker-compose exec uwsgi ./manage.py install_labels 
docker-compose exec uwsgi ./manage.py loadhashtags ocupa2app/fixtures/hashtags.yml
docker-compose exec uwsgi ./manage.py loaddata ocupa2app/fixtures/celery.json
