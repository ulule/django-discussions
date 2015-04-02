from __future__ import unicode_literals

from django.test import TestCase

from ..forms import ComposeForm, ReplyForm, FolderForm
from ..models import Discussion
from ..compat import User


class ComposeFormTests(TestCase):
    """ Test the compose form. """
    fixtures = ['users.json']

    def test_invalid_data(self):
        """
        Test the save method of :class:`ComposeForm`

        We don't need to make the ``to`` field sweat because we have done that
        in the ``fields`` test.

        """
        invalid_data_dicts = [
            # No body
            {'data': {'to': 'john',
                      'body': '',
                      'subject': ''},
             'error': ('body', ['This field is required.'])},
        ]

        for invalid_dict in invalid_data_dicts:
            form = ComposeForm(data=invalid_dict['data'])
            assert form.is_valid() is False
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])

    def test_save_discussion(self):
        """ Test valid data """
        valid_data = {'to': 'thoas,ampelmann',
                      'body': 'Body',
                      'subject': 'subject'}

        form = ComposeForm(data=valid_data)

        assert form.is_valid() is not False

        # Save the form.
        sender = User.objects.get(username='oleiade')
        discussion = form.save(sender)

        # Check if the values are set correctly
        self.assertEqual(discussion.subject, valid_data['subject'])

        self.assertEqual(discussion.messages.count(), 1)

        self.assertEqual(discussion.sender, sender)

        assert discussion.created_at is not None

        message = discussion.messages.all()[0]

        self.assertEqual(message.body, valid_data['body'])

        # Check recipients
        self.assertEqual(discussion.recipients.all()[0].username, 'ampelmann')
        self.assertEqual(discussion.recipients.all()[1].username, 'thoas')


class ReplyFormTests(TestCase):
    fixtures = ['users.json', 'messages.json']

    def test_save_message(self):
        valid_data = {'body': 'Body'}

        discussion = Discussion.objects.get(pk=1)

        form = ReplyForm(discussion=discussion, data=valid_data)

        assert form.is_valid() is True

        sender = User.objects.get(username='oleiade')

        message = form.save(sender)

        self.assertEqual(message.body, valid_data['body'])

        self.assertEqual(discussion.messages.count(), 2)

        self.assertEqual(message.sender, sender)


class FolderFormTests(TestCase):
    fixtures = ['users.json']

    def test_save_folder(self):
        valid_data = {'name': 'My folder'}

        form = FolderForm(data=valid_data)

        assert form.is_valid() is True

        sender = User.objects.get(username='oleiade')

        folder = form.save(sender)

        self.assertEqual(folder.name, valid_data['name'])
