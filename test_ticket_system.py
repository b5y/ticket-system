import os
import unittest
import psycopg2
from app import app, connect_db, verify_email_address, create_ticket, \
    change_state, add_comment, get_ticket


class TestTicketSystem(unittest.TestCase):
    def setUp(self):
        self._app = app

    def test_connect_db(self):
        assert connect_db() is not None

    def test_verify_email_address(self):
        assert verify_email_address('example@example.com') is True

    def test_create_ticket(self):
        pass

    def test_change_state(self):
        pass

    def test_add_comment(self):
        pass

    def test_get_ticket(self):
        pass


if __name__ == '__main__':
    unittest.main()
