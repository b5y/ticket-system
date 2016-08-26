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
    except TypeError:
        logger.exception("Cannot connect to the {0} database".format(DB_NAME))


def verify_id(_id=int):
    # remove after setting auto increment in database
    if not 1 <= _id <= 2147483647:
        logger.exception('Ticket number {0} is out of bound'.format(_id))
        raise ValueError()
    return True


def verify_email_address(email=basestring):
    pattern = re.compile(
        ur'^(?!\.)(""([^""\r\\]|\\[""\r\\])*""|([-a-z0-9!#$%&@\s\'*+/=?^_`{|}~]|(?<!\.)\.)*)(?<!\.)@[a-z0-9][\w\.-]*[a-z0-9]\.[a-z][a-z\.]*[a-z]$')
    if re.search(pattern, email):
        domain = email.rsplit('@', 1)[-1]
        try:
            dns.resolver.query(domain, 'MX')
            return True
        except dns.exception.DNSException:
            logger.exception('Domain name of {0} email is invalid'.format(email))
    else:
        logger.exception('Email address {0} is invalid'.format(email))
        raise ValueError()
    return False


@app.route('/')
def create_ticket(ticket_id=int, subject=basestring, text=basestring,
                  email=basestring, state=basestring):
    conn = connect_db()
    date_time = datetime.datetime
    if not conn:
        return False
    cur = conn.cursor()
    try:
        if verify_id(ticket_id) and verify_email_address(email):
            cur.execute('INSERT INTO tickets('
                        'ticket_id,'
                        'create_date,'
                        'change_date,'
                        'subject,'
                        'text,'
                        'email,'
                        'state)'
                        'VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6});'
                        .format(ticket_id,
                                date_time,
                                date_time,
                                subject,
                                text,
                                email,
                                state))
            if cur.fetchone():
                cache.set(ticket_id, cur.fetchone(), timeout=5 * 30)
            return True
    except IOError:
        logger.exception('Error creating ticket {0} with email address {1}'
                         .format(ticket_id, email))
    return False


@app.route('/')
def change_state(ticket_id=int, new_state=basestring):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    date_time = datetime.datetime
    try:
        if verify_id(ticket_id):
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
def add_comment(comment_id=int, ticket_id=int, create_date=basestring,
                email=basestring, text=basestring):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        if (verify_id(comment_id) and verify_id(ticket_id) and
                verify_email_address(email)):
            cur.execute('INSERT INTO comments('
                        'comment_id,'
                        'ticket_id,'
                        'create_date,'
                        'email,'
                        'text)'
                        'VALUES ({0}, {1}, {2}, {3}, {4})'
                        .format(comment_id, ticket_id, create_date, email, text))
            return True
    except IOError:
        logger.exception('Error add comment')
    return False


@app.route('/')
def get_ticket(ticket_id=int):
    conn = connect_db()
    if not conn:
        return None
    cur = conn.cursor()
    try:
        if verify_id(ticket_id):
            if cache.get(ticket_id):
                return cache.get(ticket_id)
            else:
                cur.execute('SELECT * FROM tickets WHERE ticket_id='.format(ticket_id))
                if cur.fetchone():
                    cache.set(ticket_id, cur.fetchone(), timeout=5 * 30)
                    return cur.fetchone()
    except IOError:
        logger.exception('Error getting ticket')
    return None


if __name__ == '__main__':
    app.run()
