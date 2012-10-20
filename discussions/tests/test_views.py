from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from discussions.forms import ComposeForm
from discussions.models import Message, Recipient, Discussion


class MessagesViewsTests(TestCase):
    fixtures = ['users', 'messages']

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

        self.failUnless(isinstance(response.context['form'],
                                   ComposeForm))

    def test_compose_post(self):
        """ ``POST`` to the compose view """
        self.client.login(username='thoas', password='$ecret')

        valid_data = {'to': 'ampelmann',
                      'body': 'Hi mister',
                      'subject': 'Hi'}

        # Check for a normal redirect
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

    def test_compose_recipients(self):
        """ A ``GET`` to the compose view with recipients """
        self.client.login(username='thoas', password='$ecret')

        valid_recipients = "thoas+oleiade"

        # Test valid recipients
        response = self.client.get(reverse('discussions_compose_to',
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
        self.failUnless(mr.read_at)

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

    def test_valid_discussion_remove(self):
        """ ``POST`` to remove a message """
        # Test that sign in is required
        response = self.client.post(reverse('discussions_remove'))
        self.assertEqual(response.status_code, 302)

        # Sign in
        self.client.login(username='thoas', password='$ecret')

        # Test that only posts are allowed
        response = self.client.get(reverse('discussions_remove'))
        self.assertEqual(response.status_code, 405)

        # Test a valid post to delete a senders message
        response = self.client.post(reverse('discussions_remove'),
                                    data={'discussion_ids': '1'})
        self.assertRedirects(response,
                             reverse('discussions_list'))
        d = Discussion.objects.get(pk=1)
        self.failUnless(d.sender_deleted_at)

        # Test a valid post to delete a recipients message and a redirect
        self.client.login(username='ampelmann', password='$ecret')
        response = self.client.post(reverse('discussions_remove'),
                                    data={'discussion_ids': '1',
                                          'next': reverse('discussions_list')})
        self.assertRedirects(response,
                             reverse('discussions_list'))
        ampelmann = User.objects.get(username='ampelmann')
        dr = d.discussionrecipient_set.get(user=ampelmann,
                                           discussion=d)
        self.failUnless(dr.deleted_at)

    def test_invalid_discussion_remove(self):
        """ ``POST`` to remove an invalid message """
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
        """ Unremove a message """
        self.client.login(username='thoas', password='$ecret')

        # Delete a message as owner
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
        """ ``GET`` the message list for a user """
        self._test_login("discussions_list")

        self.client.login(username='thoas', password='$ecret')
        response = self.client.get(reverse('discussions_list'))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'discussions/list.html')

    def test_discussion_detail_between_two_users(self):
        """ ``GET`` to a detail page between two users """
        self._test_login('discussions_list',
                         kwargs={'username': 'oleiade'})
        self.client.login(username='thoas', password='$ecret')

        response = self.client.get(reverse('discussions_list',
                                           kwargs={'username': 'oleiade'}))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'discussions/list.html')

        # Check that all the messages are marked as read.
        thoas = User.objects.get(pk=1)
        oleiade = User.objects.get(pk=3)
        unread_messages = Recipient.objects.filter(user=thoas,
                                                   discussion__sender=oleiade,
                                                   read_at__isnull=True)

        self.assertEqual(len(unread_messages), 0)
