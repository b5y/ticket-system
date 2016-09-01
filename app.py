#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import re
import psycopg2
import logging
import datetime
from flask import Flask
from contextlib import contextmanager
from psycopg2.pool import SimpleConnectionPool
from werkzeug.contrib.cache import MemcachedCache

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
DB_NAME = 'ticket_system'
cache = MemcachedCache(['127.0.0.1:11211'])
app = Flask(__name__)
connect_db_pool = SimpleConnectionPool(1, 10, database=DB_NAME,
                                       user='postgres',
                                       password='postgres',
                                       host='localhost')


@contextmanager
def get_cursor():
    conn = connect_db_pool.getconn()
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        connect_db_pool.putconn(conn)


def verify_email_address(email=basestring):
    pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    return True if re.search(pattern, email) else False


def state_variations(state=basestring):
    low_state = state.lower()
    if low_state == 'open':
        return 'answered', 'closed'
    elif low_state == 'answered':
        return 'waiting', 'closed'
    elif low_state == 'closed':
        return ''


def can_change_ticket(cur, ticket_id=int, state=None):
    cur.execute("SELECT state FROM tickets WHERE id=%s", [ticket_id])
    cur_row = cur.fetchone()
    if cur_row and isinstance(cur_row[0], basestring):
        if state:
            return True if state.lower() in state_variations(cur_row[0]) else False
        elif len(state_variations(cur_row[0])) > 0:
            return True
    return False


@app.route('/ticket/create', methods=['POST'])
def create_ticket(subject=basestring, text=basestring,
                  email=basestring, state=basestring):
    if verify_email_address(email) and state.lower() == 'open':
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with get_cursor() as cur:
            cur.execute(
                "INSERT INTO tickets(create_date, change_date, subject, _text_, email, state) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;"
                , (date_time,
                   date_time,
                   subject,
                   text,
                   email,
                   state.lower()))
            try:
                cur_row = cur.fetchone()
                if cur_row and cur_row[0]:
                    cache.set(str(cur_row[0]), cur_row, timeout=5 * 30)
            except psycopg2.ProgrammingError as p_e:
                logger.exception('Can not get created ticket and save it in cache', p_e)
            return True
    else:
        logger.exception('Can not add ticket. Email {0} or/and state {1} is/are incorrect'.format(email, state))
    return False


@app.route('/ticket/<int:ticket_id>', methods=['PUT'])
def change_state(ticket_id=int, new_state=basestring):
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_cursor() as cur:
        if can_change_ticket(cur, ticket_id=ticket_id, state=new_state):
            cur.execute("UPDATE tickets SET state=%s, change_date=%s WHERE id=%s;", (new_state, date_time, ticket_id))
        else:
            return False
        try:
            cur_row = cur.fetchone()
            if cur_row and cur_row[0]:
                cache.set(str(ticket_id), cur_row, timeout=5 * 30)
        except psycopg2.ProgrammingError as p_e:
            logger.exception('Can not get updated ticket {0} and save it in cache'.format(ticket_id), p_e)
        return True


@app.route('/comment/add', methods=['POST'])
def add_comment(ticket_id=int, email=basestring, text=basestring):
    create_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if verify_email_address(email):
        with get_cursor() as cur:
            if can_change_ticket(cur, ticket_id=ticket_id):
                cur.execute("INSERT INTO comments(ticket_id, create_date, email, _text_) VALUES (%s, %s, %s, %s);"
                            , (ticket_id, create_date, email, text))
                return True
            else:
                return False
    else:
        logger.exception('Can not add ticket. Email {0} is incorrect'.format(email))
    return False


@app.route('/ticket/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id=int):
    if cache.get(str(ticket_id)):
        return cache.get(str(ticket_id))
    else:
        with get_cursor() as cur:
            cur.execute('SELECT create_date, change_date, subject, _text_, email, state FROM tickets WHERE id=%s;',
                        [ticket_id])
            try:
                cur_row = cur.fetchone()
                if cur_row and cur_row[0]:
                    cache.set(str(ticket_id, cur_row), timeout=5 * 30)
                return cur_row
            except psycopg2.ProgrammingError as p_e:
                logger.exception('Can not get updated ticket {0} and save it in cache'.format(ticket_id), p_e)
    return None


if __name__ == '__main__':
    app.run()
