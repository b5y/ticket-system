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
            cur.execute('DROP TABLE IF EXISTS tickets CASCADE;')
            cur.execute('DROP TABLE IF EXISTS comments CASCADE;')
            try:
                cur_row = cur.fetchone()
                if cur_row and cur_row[0]:
                    print 'Tables successfully deleted'
                else:
                    print 'Can not delete tables'
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


if __name__ == '__main__':
    unittest.main()
