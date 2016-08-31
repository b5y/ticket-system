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
        new_ticket = create_ticket(subject='functionality',
                                   text='add new functionality',
                                   email='example@example.ru',
                                   state='Open')
        incorrect_email_ticket = create_ticket(subject='feature',
                                               text='add new feature',
                                               email='@@@#@example.com',
                                               state='Open')
        incorrect_state_ticket = create_ticket(subject='feature',
                                               text='add new feature',
                                               email='example@example.ru',
                                               state='In Progress')

        assert new_ticket is True
        assert incorrect_email_ticket is False
        assert incorrect_state_ticket is False

    def test_change_state(self):
        new_state = change_state(ticket_id=1, new_state='answered')
        incorrect_new_state = change_state(ticket_id=100, new_state='Open')
        assert new_state is True
        assert incorrect_new_state is False

    def test_add_comment(self):
        create_ticket(subject='functionality',
                      text='add new functionality',
                      email='example@example.ru',
                      state='Open')
        new_comment = add_comment(ticket_id=1,
                                  email='comment@example.ru',
                                  text='new comment')
        assert new_comment is True
        incorrect_new_comment = add_comment(ticket_id=100,
                                            email='comment@example.com',
                                            text='new comment')
        assert incorrect_new_comment is False
        change_state(ticket_id=1, new_state='Closed')
        add_comment_to_closed_ticket = add_comment(ticket_id=1,
                                                   email='comment@example.com',
                                                   text='new comment')
        assert add_comment_to_closed_ticket is False

    def test_get_ticket(self):
        get_ticket_ = get_ticket(ticket_id=1)
        incorrect_ticket = get_ticket(ticket_id=100)
        assert get_ticket_ is not None
        assert incorrect_ticket is None


if __name__ == '__main__':
    unittest.main()
