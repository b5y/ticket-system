#!/usr/bin/env bash

# Create virtualenv
pip install virtualenv
virtualenv env
. env/bin/activate
pip install -r requirements.txt
pip install -e .

# Set Database:
psql -c 'create database ticket_system;' -U postgres
export PGPASSWORD="postgres"
psql -f schema.sql -U postgres -d ticket_system
sudo apt-get update && sudo apt-get -y upgrade
sudo apt-get install memcached
sudo apt-get install libmemcached-dev
memcached -u memcached -d -m 30 -l 127.0.0.1 -p 11211
py.test test_ticket_system.py

# Run server with application:
# From docs: http://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html#deploying-flask
# Some useful tips: http://uwsgi-docs.readthedocs.io/en/latest/ThingsToKnow.html
uwsgi --socket 127.0.0.1:3031 --wsgi-file app.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191