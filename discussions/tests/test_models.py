from django.test import TestCase

from ..models import Message, Recipient
from ..compat import truncate_words


class MessageModelTests(TestCase):
    fixtures = ['users.json', 'messages.json']

    def test_string_formatting(self):
        """ Test the human representation of a message """
        message = Message.objects.get(pk=1)
        truncated_body = truncate_words(message.body, 10)
        self.failUnlessEqual(message.__unicode__(),
                             truncated_body)


class MessageRecipientModelTest(TestCase):
    fixtures = ['users.json', 'messages.json']

    def test_string_formatting(self):
        """ Test the human representation of a recipient """
        recipient = Recipient.objects.get(pk=1)

        valid_unicode = '%s' % (recipient.discussion)

        self.failUnlessEqual(recipient.__unicode__(),
                             valid_unicode)

    def test_new(self):
        """ Test if the message that is new is correct """
        new_message = Recipient.objects.get(pk=1)
        read_message = Recipient.objects.get(pk=2)

        self.assertFalse(new_message.is_read())
        self.assertTrue(read_message.is_read())
