# -*- coding: utf-8 -*-

import unittest
import ticket_system
import psycopg2

from ticket_system.app import (get_cursor,
                               verify_email_address,
                               logger)


class TestTicketSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ticket_system.app.config['TESTING'] = True
        cls.app = ticket_system.app.test_client()

    @classmethod
    def tearDownClass(cls):
        with get_cursor() as cur:
            with open('schema.sql', 'r') as fd:
                cur.execute(fd.read())
                try:
                    cur_row = cur.fetchone()
                    if cur_row and cur_row[0]:
                        print 'Tables successfully deleted'
                    else:
                        print 'Can not get access to tables'
                except psycopg2.ProgrammingError as p_e:
                    logger.exception('tearDownClass: There is no data in database', p_e)

    def test_get_cursor(self):
        with get_cursor() as cur:
            self.assertIsNot(cur, None)

    def test_empty_db(self):
        rv = self.app.get('/')
        assert rv.status_code == 200

    def test_verify_email_address(self):
        self.assertTrue(verify_email_address('example@example.com'))
        self.assertFalse(verify_email_address('example@.example.com'))

    def test_create_ticket(self):
        rv = self.app.post('/ticket', data=dict(
            subject='functionality',
            _text_='add new functionality',
            email='example@example.ru',
            state='open',
        ))
        self.assertNotIn(b'No entries here so far', rv.data)
        self.assertIn('Open', rv.data)
        self.assertIn('functionality', rv.data)
        self.assertIn('example@example.ru', rv.data)
        self.assertIn('add new functionality', rv.data)
        rv = self.app.post('/ticket', data=dict(
            subject='performance',
            _text_='add new feature',
            email='example@example.ru',
            state='answered',
        ))
        self.assertIn('null', rv.data)

    def test_add_comment(self):
        self.app.post('/ticket', data=dict(
            subject='performance',
            _text_='add new feature',
            email='example@example.com',
            state='open',
        ))
        rv = self.app.post('/ticket/1/comment', data=dict(
            email='example1@example.ru',
            _text_='great ticket!',
        ))
        self.assertNotIn(b'No entries here so far', rv.data)
        self.assertIn('"ticket_id": 1', rv.data)

    def test_get_ticket(self):
        rv = self.app.get('/ticket/1')
        self.assertNotIn(b'No entries here so far', rv.data)
        self.assertIn('Open', rv.data)
        self.assertIn('performance', rv.data)
        self.assertIn('example@example.com', rv.data)
        self.assertIn('add new feature', rv.data)


if __name__ == '__main__':
    unittest.main()
