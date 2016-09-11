# -*- coding: utf-8 -*-

from __future__ import with_statement

import re
import psycopg2
import logging
import datetime

from flask import Flask, request, jsonify, make_response
from contextlib import contextmanager
from psycopg2.pool import SimpleConnectionPool
from werkzeug.contrib.cache import MemcachedCache

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
DB_NAME = 'ticket_system'
cache = MemcachedCache(['127.0.0.1:11211'])
app = Flask(__name__)
connect_db_pool = SimpleConnectionPool(minconn=1, maxconn=10,
                                       database=DB_NAME,
                                       user='postgres',
                                       password='postgres',
                                       host='localhost')


@contextmanager
def get_cursor(db=connect_db_pool):
    conn = db.getconn()
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        db.putconn(conn)


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
        else:
            return False
    return False


def _make_response(ticket_id=None, data=None):
    if not data:
        return make_response(jsonify({'ticket_id': ticket_id}))
    elif not ticket_id:
        return make_response(jsonify({'data': data}))
    elif not data and not ticket_id:
        return make_response()
    return make_response(jsonify({'ticket_id': ticket_id, 'data': data}))


@app.route('/')
def index():
    return 'Index page'


@app.route('/ticket', methods=['POST'])
def create_ticket():
    data = request.form
    if verify_email_address(data['email']) and data.get('state').lower() == 'open':
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with get_cursor() as cur:
            cur.execute(
                "INSERT INTO tickets(create_date, change_date, subject, _text_, email, state) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;"
                , (date_time,
                   date_time,
                   data.get('subject'),
                   data.get('_text_'),
                   data.get('email'),
                   data.get('state').title()))
            try:
                cur_row = cur.fetchone()
                if cur_row and cur_row[0]:
                    cache.set(str(cur_row[0]), cur_row, timeout=5 * 30)
                    return _make_response(ticket_id=cur_row[0], data=cur_row)
            except psycopg2.ProgrammingError as p_e:
                logger.exception('Can not get created ticket and save it in cache', p_e)
    else:
        logger.exception('Can not add ticket. Email {0} or/and state {1} is/are incorrect'.format(data.get('email'),
                                                                                                  data.get('state')))
        return _make_response()


@app.route('/ticket/<int:id>', methods=['PUT'])
def change_state():
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = request.values
    ticket_id = data.get('id')
    with get_cursor() as cur:
        if can_change_ticket(cur, ticket_id=ticket_id, state=data.get('state')):
            cur.execute("UPDATE tickets SET state=%s, change_date=%s WHERE id=%s;",
                        (data.get('state'), date_time, ticket_id))
        else:
            return False
        try:
            cur_row = cur.fetchone()
            if cur_row and cur_row[0]:
                cache.set(str(ticket_id), cur_row, timeout=5 * 30)
                return _make_response(ticket_id=cur_row[0], data=cur_row)
        except psycopg2.ProgrammingError as p_e:
            logger.exception('Can not get updated ticket {0} and save it in cache'.format(ticket_id), p_e)
        return _make_response()


@app.route('/comment', methods=['POST'])
def add_comment():
    create_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = request.form
    ticket_id = data.get('ticket_id')
    if verify_email_address(data.get('email')):
        with get_cursor() as cur:
            if can_change_ticket(cur, ticket_id=ticket_id):
                cur.execute("INSERT INTO comments(ticket_id, create_date, email, _text_) VALUES (%s, %s, %s, %s);"
                            , (ticket_id, create_date, data.get('email'), data.get('email')))
                return _make_response(ticket_id=ticket_id)
            else:
                return _make_response()
    else:
        logger.exception('Can not add ticket. Email {0} is incorrect'.format(data.get('email')))
    return _make_response()


@app.route('/ticket/<int:id>', methods=['GET'])
def get_ticket():
    ticket_id = request.args.get('id')
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
                return _make_response(ticket_id=cur_row[0], data=cur_row)
            except psycopg2.ProgrammingError as p_e:
                logger.exception('Can not get updated ticket {0} and save it in cache'.format(ticket_id), p_e)
    return _make_response()


if __name__ == '__main__':
    app.run()
