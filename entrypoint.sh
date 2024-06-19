#!/bin/bash

if [ "$#" -eq 0 ]; then
    exec python manage.py runserver --host=0.0.0.0 --port=80
else
    exec "$@"
fi
