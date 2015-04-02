from __future__ import unicode_literals

from django.test import TestCase
from django.template import Context, Template

from ..compat import User


class TemplateTagsTests(TestCase):
    fixtures = ['users.json', 'messages.json']

    def test_get_unread_message_count_for(self):
        user = User.objects.get(pk=1)

        t = Template("{% load discussions_tags %}{% get_unread_message_count_for user as message_count %}{{ message_count }}")
        c = Context({
            'user': user
        })
        self.assertEqual('1', t.render(c))

    def test_get_unread_message_count_between(self):
        thoas = User.objects.get(pk=1)
        ampelmann = User.objects.get(pk=2)

        t = Template("{% load discussions_tags %}{% get_unread_message_count_between user_1 and user_2 as message_count %}{{ message_count }}")
        c = Context({
            'user_1': thoas,
            'user_2': ampelmann
        })
        self.assertEqual('0', t.render(c))

    def test_get_folders_for(self):
        user = User.objects.get(pk=1)

        t = Template("{% load discussions_tags %}{% get_folders_for user as folders %}{% for folder in folders %}{{ folder.name }}{% endfor %}")
        c = Context({
            'user': user
        })

        self.assertEqual('My folder', t.render(c))

        c = Context({
            'user': User.objects.get(pk=2)
        })

        self.assertEqual('', t.render(c))  # return nothing
