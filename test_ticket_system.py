import unittest
from app import connect_db, verify_email_address, create_ticket, \
    change_state, add_comment, get_ticket


class TestTicketSystem(unittest.TestCase):
    def test_connect_db(self):
        self.assertIsNot(connect_db(), None)

    def test_verify_email_address(self):
        self.assertTrue(verify_email_address('example@example.com'))

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

        self.assertTrue(new_ticket)
        self.assertFalse(incorrect_email_ticket)
        self.assertFalse(incorrect_state_ticket)

    def test_change_state(self):
        create_ticket(subject='functionality',
                      text='add new functionality',
                      email='example@example.ru',
                      state='Open')
        new_state = change_state(ticket_id=2, new_state='answered')
        incorrect_new_state = change_state(ticket_id=100, new_state='Open')
        self.assertTrue(new_state)
        self.assertFalse(incorrect_new_state)

    def test_add_comment(self):
        create_ticket(subject='functionality',
                      text='add new functionality',
                      email='example@example.ru',
                      state='Open')
        new_comment = add_comment(ticket_id=1,
                                  email='comment@example.ru',
                                  text='new comment')
        self.assertTrue(new_comment)
        incorrect_new_comment = add_comment(ticket_id=100,
                                            email='comment@example.com',
                                            text='new comment')
        self.assertFalse(incorrect_new_comment)
        change_state(ticket_id=1, new_state='Closed')
        add_comment_to_closed_ticket = add_comment(ticket_id=1,
                                                   email='comment@example.com',
                                                   text='new comment')
        self.assertFalse(add_comment_to_closed_ticket)

    def test_get_ticket(self):
        get_ticket_ = get_ticket(ticket_id=1)
        incorrect_ticket = get_ticket(ticket_id=100)
        self.assertIsNot(get_ticket_, None)
        self.assertIs(incorrect_ticket, None)


if __name__ == '__main__':
    unittest.main()
