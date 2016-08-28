#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import psycopg2
import logging
import datetime
from flask import Flask
from werkzeug.contrib.cache import MemcachedCache

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
DB_NAME = 'ticket_system'
cache = MemcachedCache()
app = Flask(__name__)


def connect_db():
    try:
        return psycopg2.connect(database=DB_NAME,
                                user='postgres',
                                password='postgres',
                                host='localhost')
    except TypeError as t_e:
        logger.exception("Cannot connect to the {0} database".format(DB_NAME), t_e)


def verify_email_address(email=basestring):
    pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    if re.search(pattern, email):
        return True
    else:
        raise ValueError('Email address {0} is invalid'.format(email))


@app.route('/')
def create_ticket(subject=basestring, text=basestring,
                  email=basestring, state=basestring):
    conn = connect_db()
    date_time = datetime.datetime
    if not conn:
        return False
    cur = conn.cursor()
    if verify_email_address(email):
        try:
            ticket_id = cur.execute('INSERT INTO tickets('
                                    'create_date,'
                                    'change_date,'
                                    'subject,'
                                    'text,'
                                    'email,'
                                    'state)'
                                    'VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}) '
                                    'RETURNING id;'
                                    .format(date_time,
                                            date_time,
                                            subject,
                                            text,
                                            email,
                                            state))
            if cur.fetchone():
                cache.set(ticket_id, cur.fetchone(), timeout=5 * 30)
            return True
        except IOError as io_e:
            logger.exception('Error creating new data with email address {0}'
                             .format(email), io_e)
    return False


@app.route('/')
def change_state(ticket_id=int, new_state=basestring):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    date_time = datetime.datetime
    try:
        cur.execute('UPDATE tickets'
                    'SET state={0}, change_date={1} WHERE ticket_id={2};'
                    .format(new_state, date_time, ticket_id))
        if cur.fetchone():
            cache.set(ticket_id, cur.fetchone(), timeout=5 * 30)
        return True
    except IOError:
        logger.exception('Error changing state')
    return False


@app.route('/')
def add_comment(ticket_id=int, create_date=basestring,
                email=basestring, text=basestring):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    if verify_email_address(email):
        try:
            cur.execute('INSERT INTO comments('
                        'ticket_id,'
                        'create_date,'
                        'email,'
                        'text)'
                        'VALUES ({0}, {1}, {2}, {3}, {4});'
                        .format(ticket_id, create_date, email, text))
            return True
        except IOError:
            logger.exception('Error adding comment {0}'.format(text))
    else:
        raise ValueError('Invalid email address')
    return False


@app.route('/')
def get_ticket(ticket_id=int):
    conn = connect_db()
    if not conn:
        return None
    cur = conn.cursor()
    if cache.get(ticket_id):
        return cache.get(ticket_id)
    else:
        try:
            cur.execute('SELECT * FROM tickets WHERE ticket_id={0};'.format(ticket_id))
            if cur.fetchone():
                cache.set(ticket_id, cur.fetchone(), timeout=5 * 30)
                return cur.fetchone()
        except IOError:
            logger.exception('Error getting ticket {0}'.format(ticket_id))
    return None


if __name__ == '__main__':
    app.run()
