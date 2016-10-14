from __future__ import unicode_literals

from django.test import TestCase

from ..models import Message, Recipient
from ..compat import truncate_words


class MessageModelTests(TestCase):
    fixtures = ['users.json', 'messages.json']

    def test_string_formatting(self):
        """ Test the human representation of a message """
        message = Message.objects.get(pk=1)
        truncated_body = truncate_words(message.body, 10)
        self.assertEqual('%s' % message,
                         truncated_body)


class MessageRecipientModelTest(TestCase):
    fixtures = ['users.json', 'messages.json']

    def test_string_formatting(self):
        """ Test the human representation of a recipient """
        recipient = Recipient.objects.get(pk=1)

        valid_unicode = '%s' % recipient.discussion

        self.assertEqual('%s' % recipient,
                         valid_unicode)

    def test_recipients_count(self):
        recipient = Recipient.objects.get(pk=1)

        discussion = recipient.discussion

        assert discussion.recipients_count == discussion.recipients.count()

    def test_new(self):
        """ Test if the message that is new is correct """
        new_message = Recipient.objects.get(pk=1)
        read_message = Recipient.objects.get(pk=2)

        self.assertFalse(new_message.is_read())
        self.assertTrue(read_message.is_read())
