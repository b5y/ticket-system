import unittest
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
        # new_ticket = create_ticket(subject='functionality',
        #                            text='add new functionality',
        #                            email='example@example.ru',
        #                            state='In Progress')
        #
        # assert new_ticket is True
        pass

    def test_change_state(self):
        # new_state = change_state(ticket_id=3, new_state='Done')
        # assert new_state is True
        pass

    def test_add_comment(self):
        # new_comment = add_comment(ticket_id=1,
        #                           email='comment@example.ru',
        #                           text='new comment')
        # assert new_comment is True
        pass

    def test_get_ticket(self):
        # get_ticket_ = get_ticket(ticket_id=1)
        # assert get_ticket_ is not None
        pass


if __name__ == '__main__':
    unittest.main()
