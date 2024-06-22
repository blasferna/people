#!/bin/bash

if [ "$#" -eq 0 ]; then
    exec python manage.py runserver --host=0.0.0.0 --port=80
else
    if [ $# -eq 1 ] && ([[ $1 == "build" ]] || [[ $1 == "download" ]]); then
        exec python manage.py "$1"
    else
        exec "$@"
    fi
fi
