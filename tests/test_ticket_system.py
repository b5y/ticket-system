# -*- coding: utf-8 -*-

from __future__ import with_statement

import unittest
import tempfile
import ticket_system

from ticket_system.app import (connect_db_pool,
                               get_cursor,
                               verify_email_address,
                               create_ticket)


class TestTicketSystem(unittest.TestCase):
    def setUp(self):
        ticket_system.app.config['TESTING'] = True
        self.app = ticket_system.app.test_client()
        self.assertIsNotNone(connect_db_pool)

    def test_get_cursor(self):
        with get_cursor() as cur:
            self.assertIsNot(cur, None)

    def test_verify_email_address(self):
        self.assertTrue(verify_email_address('example@example.com'))

    def test_create_ticket(self):
        pass

        # def test_change_state(self):
        #     create_ticket(subject='functionality',
        #                   text='add new functionality',
        #                   email='example@example.ru',
        #                   state='Open')
        #     new_state = change_state(ticket_id=2, new_state='answered')
        #     incorrect_new_state = change_state(ticket_id=100, new_state='Open')
        #     self.assertTrue(new_state)
        #     self.assertFalse(incorrect_new_state)
        #
        # def test_add_comment(self):
        #     create_ticket(subject='functionality',
        #                   text='add new functionality',
        #                   email='example@example.ru',
        #                   state='Open')
        #     new_comment = add_comment(ticket_id=1,
        #                               email='comment@example.ru',
        #                               text='new comment')
        #     self.assertTrue(new_comment)
        #     incorrect_new_comment = add_comment(ticket_id=100,
        #                                         email='comment@example.com',
        #                                         text='new comment')
        #     self.assertFalse(incorrect_new_comment)
        #     change_state(ticket_id=1, new_state='Closed')
        #     add_comment_to_closed_ticket = add_comment(ticket_id=1,
        #                                                email='comment@example.com',
        #                                                text='new comment')
        #     self.assertFalse(add_comment_to_closed_ticket)
        #
        # def test_get_ticket(self):
        #     get_ticket_ = get_ticket(ticket_id=1)
        #     incorrect_ticket = get_ticket(ticket_id=100)
        #     self.assertIsNot(get_ticket_, None)
        #     self.assertIs(incorrect_ticket, None)


if __name__ == '__main__':
    unittest.main()
