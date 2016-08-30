#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from __future__ import with_statement

import re
import psycopg2
import logging
import datetime
import pylibmc
from flask import Flask

# from contextlib import contextmanager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
DB_NAME = 'ticket_system'
cache = pylibmc.Client(["127.0.0.1"], binary=True, behaviors={"tcp_nodelay": True, "ketama": True})
app = Flask(__name__)


def connect_db():
    try:
        conn = psycopg2.connect(database=DB_NAME,
                                user='postgres',
                                password='postgres',
                                host='localhost')
        conn.autocommit = True
        return conn
    except TypeError as t_e:
        logger.exception("Cannot connect to the {0} database".format(DB_NAME), t_e)


def verify_email_address(email=basestring):
    pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    if re.search(pattern, email):
        return True
    else:
        raise ValueError('Email address {0} is invalid'.format(email))


@app.route('/ticket/create', methods=['POST'])
def create_ticket(subject=basestring, text=basestring,
                  email=basestring, state=basestring):
    conn = connect_db()
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not conn:
        return False
    cur = conn.cursor()
    if verify_email_address(email):
        try:
            cur.execute(
                "INSERT INTO tickets(create_date, change_date, subject, text, email, state) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;"
                , (date_time,
                   date_time,
                   subject,
                   text,
                   email,
                   state))
            # Bug with fetchone? https://github.com/psycopg/psycopg2/issues/469
            try:
                cur_row = cur.fetchone()
                if cur_row and cur_row[0]:
                    cache.set(str(cur_row[0]), cur_row)
            except psycopg2.ProgrammingError as p_e:
                logger.exception('Can not get created ticket and save it in cache', p_e)
            return True
        except IOError as io_e:
            logger.exception('Error creating new data with email address {0}'
                             .format(email), io_e)
        finally:
            if conn:
                conn.close()
    return False


@app.route('/ticket/<int:ticket_id>', methods=['PUT'])
def change_state(ticket_id=int, new_state=basestring):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cur.execute("UPDATE tickets SET state=%s, change_date=%s WHERE id=%s;", (new_state, date_time, ticket_id))
        try:
            cur_row = cur.fetchone()
            if cur_row and cur_row[0]:
                cache.set(str(ticket_id), cur_row)
        except psycopg2.ProgrammingError as p_e:
            logger.exception('Can not get updated ticket {0} and save it in cache'.format(ticket_id), p_e)
        return True
    except IOError:
        logger.exception('Error changing state')
    finally:
        if conn:
            conn.close()
    return False


@app.route('/comment/add', methods=['POST'])
def add_comment(ticket_id=int, email=basestring, text=basestring):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    create_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if verify_email_address(email):
        try:
            cur.execute("INSERT INTO comments(ticket_id, create_date, email, text) VALUES (%s, %s, %s, %s);"
                        , (ticket_id, create_date, email, text))
            return True
        except IOError:
            logger.exception('Error adding comment {0}'.format(text))
        finally:
            if conn:
                conn.close()
    else:
        raise ValueError('Invalid email address')
    return False


@app.route('/ticket/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id=int):
    conn = connect_db()
    if not conn:
        return None
    cur = conn.cursor()
    if cache.get(str(ticket_id)):
        return cache.get(str(ticket_id))
    else:
        try:
            cur.execute('SELECT create_date, change_date, subject, text, email, state FROM tickets WHERE id=%s;',
                        [ticket_id])
            try:
                cur_row = cur.fetchone()
                if cur_row and cur_row[0]:
                    cache.set(str(ticket_id), cur_row)
                return cur_row
            except psycopg2.ProgrammingError as p_e:
                logger.exception('Can not get updated ticket {0} and save it in cache'.format(ticket_id), p_e)
        except IOError:
            logger.exception('Error getting ticket {0}'.format(ticket_id))
        finally:
            if conn:
                conn.close()
    return None


if __name__ == '__main__':
    app.run()


# Better approach with pool connections
# connect_db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, database=DB_NAME,
#                                                      user='postgres',
#                                                      password='postgres',
#                                                      host='localhost')
#
# @contextmanager
# def get_cursor():
#     conn = connect_db_pool()
#     try:
#         yield conn.cursor()
#     finally:
#         conn.putconn(conn)
#
# # Usage
#
# with get_cursor as cur:
#     cur.execute('...')
