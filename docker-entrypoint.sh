#!/bin/bash
set -e

python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
python manage.py createcachetable
python manage.py makemessages -a
python manage.py compilemessages

exec "$@"