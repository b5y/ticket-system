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
psql -f ./ticket_system/schema.sql -U postgres -d ticket_system
# Add uWSGI to PPA:
sudo add-apt-repository ppa:uwsgi/release
sudo apt-get update && sudo apt-get -y upgrade
# Install required packages:
sudo apt-get install uwsgi
sudo apt-get install memcached
sudo apt-get install libmemcached-dev
# Run uwsgi to check that everything is OK
(sleep 5; echo uwsgi --socket 127.0.0.1:3031 --wsgi-file app.py --callable app --master) &
memcached -u memcached -d -m 30 -l 127.0.0.1 -p 11211
# Creating folders relating to running uwsgi:
sudo mkdir /var/run/flask-uwsgi
sudo chown www-data:www-data /var/run/flask-uwsgi
sudo mkdir /var/log/flask-uwsgi
sudo chown www-data:www-data /var/log/flask-uwsgi
sudo mkdir /etc/flask-uwsgi
sudo cp flask-uwsgi.conf /etc/init/flask-uwsgi.conf
sudo cp flask-uwsgi.ini /etc/flask-uwsgi/flask-uwsgi.ini
sudo service uwsgi start
py.test test_ticket_system.py
sudo service uwsgi stop

# Run server with application:
# From docs: http://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html#deploying-flask
# Some useful tips: http://uwsgi-docs.readthedocs.io/en/latest/ThingsToKnow.html
# uwsgi --socket 127.0.0.1:3031 --wsgi-file app.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191