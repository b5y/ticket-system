#!/usr/bin/env bash

# Create virtualenv
virtualenv env
. env/bin/activate
pip install -r requirements.txt
pip install -e .

# Set Database:
psql -c 'create database ticket_system;' -U postgres
export PGPASSWORD="postgres"
psql -f schema.sql -U postgres -d ticket_system

# Run server with application:
# From docs: http://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html#deploying-flask
# Some useful tips: http://uwsgi-docs.readthedocs.io/en/latest/ThingsToKnow.html
uwsgi --socket 127.0.0.1:3031 --wsgi-file app.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191