from django.test import TestCase
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from ..forms import ComposeForm, FolderForm
from ..models import Message, Recipient, Discussion, Folder
from ..compat import User


class DiscussionsViewsTests(TestCase):
    fixtures = ['users.json', 'messages.json']

    def _test_login(self, named_url, **kwargs):
        """ Test that the view requires login """
        response = self.client.get(reverse(named_url, **kwargs))
        self.assertEqual(response.status_code, 302)

    def test_compose(self):
        """ A ``GET`` to the compose view """
        # Login is required.
        self._test_login('discussions_compose')

        # Sign in
        self.client.login(username='thoas', password='$ecret')
        response = self.client.get(reverse('discussions_compose'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'discussions/form.html')

        self.assertTrue(isinstance(response.context['form'],
                                   ComposeForm))

    def test_compose_post(self):
        """ ``POST`` to the compose view """
        self.client.login(username='thoas', password='$ecret')

        valid_data = {'to': 'ampelmann',
                      'body': 'Hi mister',
                      'subject': 'Hi'}

        response = self.client.post(reverse('discussions_compose'),
                                    data=valid_data)

        self.assertEqual(response.status_code, 200)

        valid_data['submit'] = 'submit'

        response = self.client.post(reverse('discussions_compose'),
                                    data=valid_data)

        self.assertRedirects(response,
                             reverse('discussions_detail',
                                     kwargs={'discussion_id': 3}))

        # Check for a requested redirect
        valid_data['next'] = reverse('discussions_compose')
        response = self.client.post(reverse('discussions_compose'),
                                    data=valid_data)
        self.assertRedirects(response,
                             valid_data['next'])

    def test_compose_recipients_get(self):
        """ A ``GET`` to the compose view with recipients """
        self.client.login(username='thoas', password='$ecret')

        valid_recipients = "thoas+oleiade"

        # Test valid recipients
        response = self.client.get(reverse('discussions_compose',
                                           kwargs={'recipients': valid_recipients}))

        self.assertEqual(response.status_code, 200)

        # Test the users
        oleiade = User.objects.get(username='oleiade')
        thoas = User.objects.get(username='thoas')
        self.assertEqual(response.context['recipients'][0], oleiade)
        self.assertEqual(response.context['recipients'][1], thoas)

        # Test that the initial data of the form is set.
        self.assertEqual(response.context['form'].initial['to'],
                         [oleiade, thoas])

    def test_compose_recipients_post(self):
        """ A ``POST`` to the compose view with recipients """
        self.client.login(username='thoas', password='$ecret')

        valid_recipients = "thoas+oleiade"

        # Test valid recipients
        response = self.client.post(reverse('discussions_compose'), data={
            'recipients': valid_recipients
        })

        self.assertEqual(response.status_code, 200)

        # Test the users
        oleiade = User.objects.get(username='oleiade')
        thoas = User.objects.get(username='thoas')
        self.assertEqual(response.context['recipients'][0], oleiade)
        self.assertEqual(response.context['recipients'][1], thoas)

        # Test that the initial data of the form is set.
        self.assertEqual(response.context['form'].initial['to'],
                         [oleiade, thoas])

    def test_discussion_detail(self):
        """ A ``GET`` to the detail view """
        self._test_login('discussions_detail',
                         kwargs={'discussion_id': 2})

        # Sign in
        self.client.login(username='ampelmann', password='$ecret')
        response = self.client.get(reverse('discussions_detail',
                                   kwargs={'discussion_id': 1}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'discussions/detail.html')

        # Test that the message is read.
        ampelmann = User.objects.get(pk=2)
        mr = Recipient.objects.get(discussion=Discussion.objects.get(pk=1),
                                   user=ampelmann)

        assert mr.read_at is not None

    def test_discussion_detail_new_message(self):
        self.client.login(username='ampelmann', password='$ecret')
        discussion = Discussion.objects.get(pk=1)

        response = self.client.post(discussion.get_absolute_url(),
                                    data={
                                        'body': 'My reply'
                                    })
        self.assertRedirects(response, discussion.get_absolute_url())

        self.assertEqual(discussion.messages.count(), 2)

        ampelmann = User.objects.get(username='ampelmann')

        message = discussion.messages.get(sender=ampelmann)

        self.assertEqual(message.body, 'My reply')

    def test_valid_discussion_move(self):
        """ ``POST`` to move a discussion into a folder """
        # Test that sign in is required

        folder = Folder.objects.get(pk=1)

        url = reverse('discussions_move', kwargs={
            'folder_id': folder.pk
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Sign in
        self.client.login(username='thoas', password='$ecret')

        # Test that only posts are allowed
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(url,
                                    data={'discussion_ids': '1'})
        self.assertRedirects(response,
                             reverse('discussions_list'))

        user = User.objects.get(username='thoas')

        recipient = Recipient.objects.get(discussion=1, user=user)

        self.assertEqual(recipient.folder, folder)

    def test_invalid_discussion_move(self):
        folder = Folder.objects.get(pk=1)

        url = reverse('discussions_move', kwargs={
            'folder_id': folder.pk
        })

        self.client.login(username='ampelmann', password='$ecret')

        response = self.client.post(url,
                                    data={'discussion_ids': '1'})

        self.assertEqual(response.status_code, 404)

    def test_valid_discussion_mark_as_read(self):
        """ ``POST`` to mark a discussion as read """
        # Test that sign in is required
        response = self.client.post(reverse('discussions_mark_as_read'))
        self.assertEqual(response.status_code, 302)

        # Sign in
        self.client.login(username='thoas', password='$ecret')

        # Test that only posts are allowed
        response = self.client.get(reverse('discussions_mark_as_read'))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse('discussions_mark_as_read'),
                                    data={'discussion_ids': '1'})
        self.assertRedirects(response,
                             reverse('discussions_list'))

        recipient = Discussion.objects.get(pk=1).recipient_set.get(user=User.objects.get(pk=1))

        self.assertTrue(recipient.is_read())

    def test_valid_discussion_mark_as_unread(self):
        """ ``POST`` to mark a discussion as unread"""
        # Test that sign in is required
        response = self.client.post(reverse('discussions_mark_as_unread'))
        self.assertEqual(response.status_code, 302)

        # Sign in
        self.client.login(username='thoas', password='$ecret')

        # Test that only posts are allowed
        response = self.client.get(reverse('discussions_mark_as_unread'))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse('discussions_mark_as_unread'),
                                    data={'discussion_ids': '1'})
        self.assertRedirects(response,
                             reverse('discussions_list'))

        recipient = Discussion.objects.get(pk=1).recipient_set.get(user=User.objects.get(pk=1))

        self.assertFalse(recipient.is_read())

    def test_valid_discussion_leave(self):
        """ ``POST`` to leave a discussion
        # Test that sign in is required'"""
        response = self.client.post(reverse('discussions_leave'))
        self.assertEqual(response.status_code, 302)

        # Sign in
        self.client.login(username='ampelmann', password='$ecret')

        # Test that only posts are allowed
        response = self.client.get(reverse('discussions_leave'))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse('discussions_leave'),
                                    data={'discussion_ids': [1]})

        self.assertRedirects(response,
                             reverse('discussions_list'))

        self.assertFalse(Discussion.objects.get(pk=1).recipients.filter(pk=2).exists())

    def test_invalid_discussion_leave_when_sender(self):
        """ ``POST`` to leave a discussion
        # Test that sign in is required'"""
        response = self.client.post(reverse('discussions_leave'))
        self.assertEqual(response.status_code, 302)

        # Sign in
        self.client.login(username='thoas', password='$ecret')

        # Test that only posts are allowed
        response = self.client.get(reverse('discussions_leave'))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse('discussions_leave'),
                                    data={'discussion_ids': [1]})

        self.assertRedirects(response,
                             reverse('discussions_list'))

        self.assertTrue(Discussion.objects.get(pk=1).recipients.filter(pk=2).exists())

    def test_valid_discussion_remove(self):
        """ ``POST`` to remove a discussion """
        # Test that sign in is required
        response = self.client.post(reverse('discussions_remove'))
        self.assertEqual(response.status_code, 302)

        # Sign in
        self.client.login(username='thoas', password='$ecret')

        # Test that only posts are allowed
        response = self.client.get(reverse('discussions_remove'))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse('discussions_remove'),
                                    data={'discussion_ids': '1'})
        self.assertRedirects(response,
                             reverse('discussions_list'))
        d = Discussion.objects.get(pk=1)
        assert d.sender_deleted_at is not None

        self.client.login(username='ampelmann', password='$ecret')
        response = self.client.post(reverse('discussions_remove'),
                                    data={'discussion_ids': '1',
                                          'next': reverse('discussions_list')})
        self.assertRedirects(response,
                             reverse('discussions_list'))
        ampelmann = User.objects.get(username='ampelmann')
        dr = d.recipient_set.get(user=ampelmann,
                                 discussion=d)

        assert dr.deleted_at is not None

    def test_invalid_discussion_remove(self):
        """ ``POST`` to remove an invalid discussion """
        # Sign in
        self.client.login(username='thoas', password='$ecret')

        bef_len = Message.objects.filter(sender_deleted_at__isnull=False).count()
        response = self.client.post(reverse('discussions_remove'),
                                    data={'discussion_ids': ['a', 'b']})

        # The program should play nice, nothing happened.
        af_len = Message.objects.filter(sender_deleted_at__isnull=False).count()
        self.assertRedirects(response,
                             reverse('discussions_list'))
        self.assertEqual(bef_len, af_len)

    def test_valid_discussion_remove_multiple(self):
        """ ``POST`` to remove multiple messages """
        # Sign in
        self.client.login(username='thoas', password='$ecret')
        response = self.client.post(reverse('discussions_remove'),
                                    data={'discussion_ids': [1, 2]})
        self.assertRedirects(response,
                             reverse('discussions_list'))

        discussion_list = Discussion.objects.filter(pk__in=['1', '2'],
                                                    sender_deleted_at__isnull=False)

        # thoas has created only one discussion (see fixtures)
        self.assertEqual(discussion_list.count(), 1)

    def test_discussion_unremove(self):
        """ Unremove a discussion """
        self.client.login(username='thoas', password='$ecret')

        # Delete a discussion as owner
        response = self.client.post(reverse('discussions_unremove'),
                                    data={'discussion_pks': [1, ]})

        self.assertRedirects(response,
                             reverse('discussions_list'))

        # Delete the message as a recipient
        response = self.client.post(reverse('discussions_unremove'),
                                    data={'discussion_pks': [2, ]})

        self.assertRedirects(response,
                             reverse('discussions_list'))

    def test_discussion_list(self):
        """ ``GET`` the discussion list for a user """
        self._test_login("discussions_list")

        self.client.login(username='thoas', password='$ecret')
        response = self.client.get(reverse('discussions_list'))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'discussions/list.html')

    def test_discussion_sent(self):
        """ ``GET`` the message list for a user """
        self._test_login("discussions_sent")

        self.client.login(username='thoas', password='$ecret')
        response = self.client.get(reverse('discussions_sent'))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'discussions/sent.html')

    def test_discussion_deleted(self):
        """ ``GET`` the message list for a user """
        self._test_login("discussions_deleted")

        self.client.login(username='thoas', password='$ecret')
        response = self.client.get(reverse('discussions_deleted'))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'discussions/deleted.html')

    def test_discussion_unread(self):
        """ ``GET`` the message list for a user """
        self._test_login("discussions_unread")

        self.client.login(username='thoas', password='$ecret')
        response = self.client.get(reverse('discussions_unread'))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'discussions/unread.html')

    def test_discussion_read(self):
        """ ``GET`` the message list for a user """
        self._test_login("discussions_unread")

        self.client.login(username='thoas', password='$ecret')
        response = self.client.get(reverse('discussions_read'))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'discussions/read.html')

    def test_discussion_detail_between_two_users(self):
        """ ``GET`` to a detail page between two users """
        self._test_login('discussions_list')
        self.client.login(username='thoas', password='$ecret')

        response = self.client.get(reverse('discussions_list'))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'discussions/list.html')

        # Check that all the messages are marked as read.
        thoas = User.objects.get(pk=1)
        oleiade = User.objects.get(pk=3)
        unread_messages = Recipient.objects.filter(user=thoas,
                                                   discussion__sender=oleiade,
                                                   read_at__isnull=True)

        self.assertEqual(len(unread_messages), 0)

    def test_folder_list(self):
        """ ``GET`` the discussion list for a user """
        self._test_login("discussions_folders_list")

        self.client.login(username='thoas', password='$ecret')
        response = self.client.get(reverse('discussions_folders_list'))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'discussions/folder/list.html')

    def test_folder_create(self):
        self._test_login('discussions_folder_create')

        self.client.login(username='thoas', password='$ecret')

        response = self.client.get(reverse('discussions_folder_create'))

        self.assertEqual(response.status_code, 200)

        self.assertTrue(isinstance(response.context['form'], FolderForm))
        self.assertTemplateUsed(response,
                                'discussions/folder/create.html')

        data = {
            'name': 'My folder'
        }

        response = self.client.post(reverse('discussions_folder_create'), data=data)

        self.assertEqual(Folder.objects.count(), 2)

        folder = Folder.objects.get(pk=2)

        self.assertEqual(folder.name, data['name'])

        self.assertRedirects(response,
                             reverse('discussions_list'))

    def test_folder_update(self):
        folder = Folder.objects.get(pk=1)

        self._test_login('discussions_folder_update', kwargs={
            'folder_id': folder.pk
        })

        self.client.login(username='thoas', password='$ecret')

        response = self.client.get(reverse('discussions_folder_update', kwargs={
            'folder_id': folder.pk
        }))

        self.assertEqual(response.status_code, 200)

        self.assertTrue(isinstance(response.context['form'], FolderForm))
        self.assertTemplateUsed(response,
                                'discussions/folder/update.html')

        data = {
            'name': 'My folder new name'
        }

        response = self.client.post(reverse('discussions_folder_update', kwargs={
            'folder_id': folder.pk
        }), data=data)

        folder = Folder.objects.get(pk=1)

        self.assertEqual(folder.name, data['name'])

        self.assertRedirects(response,
                             reverse('discussions_list', kwargs={
                                 'folder_id': folder.pk
                             }))

    def test_discussion_move_to_folder(self):
        response = self.client.post(reverse('discussions_move',
                                            kwargs={'folder_id': 1}),
                                    data={'discussion_ids': [2]})
        self.assertEqual(response.status_code, 302)

        # Sign in
        self.client.login(username='thoas', password='$ecret')

        # Test that only posts are allowed
        response = self.client.get(reverse('discussions_move',
                                           kwargs={'folder_id': 1}),
                                   data={'discussion_ids': [2]})
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse('discussions_move',
                                            kwargs={'folder_id': 1}),
                                    data={'discussion_ids': [2]})
        recipient = Recipient.objects.get(pk=2)

        folder = Folder.objects.get(pk=1)

        self.assertEqual(recipient.folder, folder)

    def test_discussion_move_to_mailbox(self):
        response = self.client.post(reverse('discussions_move'),
                                    data={'discussion_ids': [3]})
        self.assertEqual(response.status_code, 302)

        # Sign in
        self.client.login(username='thoas', password='$ecret')

        # Test that only posts are allowed
        response = self.client.get(reverse('discussions_move'),
                                   data={'discussion_ids': [3]})
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse('discussions_move'),
                                    data={'discussion_ids': [3]})
        recipient = Recipient.objects.get(pk=3)

        self.assertEqual(recipient.folder, None)

    def test_folder_remove_pk_does_not_exist(self):
        # Sign in
        self.client.login(username='thoas', password='$ecret')

        response = self.client.post(reverse('discussions_folder_remove',
                                    kwargs={'folder_id': 35}))

        self.assertEqual(response.status_code, 404)

    def test_valid_folder_remove(self):
        response = self.client.post(reverse('discussions_folder_remove',
                                            kwargs={'folder_id': 1}))
        self.assertEqual(response.status_code, 302)

        # Sign in
        self.client.login(username='thoas', password='$ecret')

        # Test that only posts are allowed
        response = self.client.get(reverse('discussions_folder_remove',
                                           kwargs={'folder_id': 1}))
        self.assertEqual(response.status_code, 405)

        folder = Folder.objects.get(pk=1)
        related_recipient = Recipient.objects.filter(folder=folder)

        response = self.client.post(reverse('discussions_folder_remove',
                                            kwargs={'folder_id': 1}))

        for recipient in related_recipient:
            self.assertEqual(recipient.folder, None)

        self.assertRedirects(response,
                             reverse('discussions_list'))

        self.assertFalse(Folder.objects.filter(pk=1).exists())
