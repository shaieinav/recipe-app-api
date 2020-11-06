from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """
        Test waiting for DB when DB is available.
        Simulating the behavior of django when the DB is available by
        overwriting the behavior of the connection handler and return
        True and not throwing an exception.
        """

        # retrieving the default db via the connection handler and mocking
        # the behavior of this __getitem__ using the patch.
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            # call our wait_for_db management command
            call_command('wait_for_db')
            # check to see that gi was called once
            self.assertEqual(gi.call_count, 1)

    # replaces the behavior of time.sleep in order to not delay the tests.
    # adding a parameter for time.sleep, ts, for function to pass with the
    # patch.
    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """
        Test waiting for DB.
        Testing to see that the wait_for_db command will try the DB 5 times
        and then in the 6th time it will be succesful and continue.
        """

        # retrieving the default db via the connection handler and mocking
        # the behavior of this __getitem__ using the patch.
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # raise OperationalError 5 times, and then on the 6th time don't
            gi.side_effect = [OperationalError] * 5 + [True]
            # call our wait_for_db management command
            call_command('wait_for_db')
            # check to see that gi was called 6 times
            self.assertEqual(gi.call_count, 6)
