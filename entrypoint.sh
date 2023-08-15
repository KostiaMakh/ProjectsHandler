#!/bin/sh

python3 manage.py migrate


# Collect static files if on production
if [ "$1" = production ]; then
    python3 manage.py collectstatic --noinput
    gunicorn config.wsgi -c deploy_config/gunicorn.cfg --certfile=deploy_config/certs/fullchain.pem --keyfile=deploy_config/certs/privkey.pem
elif [ "$1" = staging ]; then
    python3 manage.py collectstatic --noinput
    gunicorn config.wsgi -c deploy_config/gunicorn.cfg --reload
elif [ "$1" = development ]; then
    gunicorn config.wsgi -c deploy_config/gunicorn.cfg --reload
else
    echo "No target environment specified"
fi
