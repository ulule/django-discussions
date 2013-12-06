from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from discussions.managers import (DiscussionManager, ContactManager,
                                  RecipientManager, MessageManager)

from ..utils import tznow

from model_utils import Choices


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


@python_2_unicode_compatible
class Contact(models.Model):
    """
    Contact model.

    A contact is a user to whom a user has send a message to or
    received a message from.

    """
    from_user = models.ForeignKey(AUTH_USER_MODEL,
                                  verbose_name=_('from user'),
                                  related_name=('from_contact_users'))

    to_user = models.ForeignKey(AUTH_USER_MODEL,
                                verbose_name=_('to user'),
                                related_name=('to_contact_users'))

    latest_discussion = models.ForeignKey('Discussion',
                                          verbose_name=_("latest discussion"))

    objects = ContactManager()

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['latest_discussion']
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')
        app_label = 'discussions'

    def __str__(self):
        return (_('%(from_user)s and %(to_user)s')
                % {'from_user': self.from_user.username,
                   'to_user': self.to_user.username})

    def opposite_user(self, user):
        """
        Returns the user opposite of the user that is given

        :param user:
            A Django :class:`User`.

        :return:
            A Django :class:`User`.

        """
        if self.from_user == user:
            return self.to_user

        return self.from_user


class Recipient(models.Model):
    """
    Intermediate model to allow per recipient marking as
    deleted, read etc. of a message.

    """
    STATUS = Choices((0, 'read', _('read')),
                     (1, 'unread', _('unread')),
                     (2, 'deleted', _('deleted')))

    user = models.ForeignKey(AUTH_USER_MODEL,
                             verbose_name=_('recipient'))

    discussion = models.ForeignKey('Discussion',
                                   verbose_name=_('discussion'))

    folder = models.ForeignKey('Folder',
                               verbose_name=_('folder'),
                               null=True, blank=True,
                               related_name='recipients')

    read_at = models.DateTimeField(_('read at'),
                                   null=True,
                                   blank=True)

    deleted_at = models.DateTimeField(_('recipient deleted at'),
                                      null=True,
                                      blank=True)

    status = models.PositiveSmallIntegerField(choices=STATUS,
                                              default=STATUS.unread,
                                              verbose_name=_('Status'),
                                              db_index=True)

    objects = RecipientManager()

    class Meta:
        verbose_name = _('recipient')
        verbose_name_plural = _('recipients')
        app_label = 'discussions'

    def __unicode__(self):
        return (_('%(discussion)s')
                % {'discussion': self.discussion})

    def is_read(self):
        """ Returns a boolean whether the recipient has read the message """
        return self.status == self.STATUS.read

    def is_deleted(self):
        """ Returns a boolean whether the recipient has deleted the message """
        return self.status == self.STATUS.deleted

    def mark_as_deleted(self, commit=True):
        self.deleted_at = tznow()
        self.status = self.STATUS.deleted

        if commit:
            self.save()

    def mark_as_read(self, commit=True):
        self.read_at = tznow()
        self.status = self.STATUS.read

        if commit:
            self.save()


@python_2_unicode_compatible
class Discussion(models.Model):
    """ Private message model, from user to user(s) """
    sender = models.ForeignKey(AUTH_USER_MODEL,
                               related_name='sent_discussions',
                               verbose_name=_('sender'))

    recipients = models.ManyToManyField(AUTH_USER_MODEL,
                                        through='Recipient',
                                        related_name='received_discussions',
                                        verbose_name=_('recipients'))

    objects = DiscussionManager()

    created_at = models.DateTimeField(_('created at'),
                                      auto_now_add=True)

    updated_at = models.DateTimeField(_('updated at'),
                                      null=True, blank=True)

    sender_deleted_at = models.DateTimeField(_("sender deleted at"),
                                             null=True,
                                             blank=True)

    latest_message = models.ForeignKey('Message', null=True, blank=True, related_name='latest_discussions')

    subject = models.CharField(max_length=255)

    objects = DiscussionManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('discussion')
        verbose_name_plural = _('discussions')
        permissions = (
            ('can_view', 'Can view'),
        )
        app_label = 'discussions'

    def __str__(self):
        return 'Discussion opened by %s' % self.sender

    def save_recipients(self, to_user_list):
        """
        Save the recipients for this message

        :param to_user_list:
            A list which elements are :class:`User` to whom the message is for.

        :return:
            Boolean indicating if any users are saved.

        """
        created = False
        for user in to_user_list:
            Recipient.objects.create(user=user,
                                     discussion=self)
            created = True
        return created

    def update_contacts(self, to_user_list):
        """
        Updates the contacts that are used for this message.

        :param to_user_list:
            List of Django :class:`User`.

        :return:
            A boolean if a user is contact is updated.

        """
        updated = False
        for user in to_user_list:
            Contact.objects.update_contact(self.sender,
                                           user,
                                           self)
            updated = True
        return updated

    def add_message(self, body, sender=None, commit=True):
        if not sender:
            sender = self.sender

        m = Message(sender=sender,
                    body=body,
                    discussion=self)
        m.save()

        self.recipient_set.exclude(user=sender).update(status=Recipient.STATUS.unread)

        self.updated_at = tznow()

        if commit:
            self.save()

        return m

    def get_absolute_url(self):
        return reverse('discussions_detail', kwargs={
            'discussion_id': self.pk
        })

    def can_view(self, user):
        if not user or not user.is_authenticated():
            return False

        if (user.is_staff or user.is_superuser or
            (user.id in [u['id']
                         for u in self.recipients.values('id')])):
            return True

        return user.has_perm('discussions.can_view')


@python_2_unicode_compatible
class Message(models.Model):
    """ Private message model, from user to user(s) """
    sender = models.ForeignKey(AUTH_USER_MODEL,
                               related_name='sent_messages',
                               verbose_name=_('sender'))

    discussion = models.ForeignKey('Discussion',
                                   related_name='messages',
                                   verbose_name=_('discussion'))

    body = models.TextField(_('body'))

    sent_at = models.DateTimeField(_('sent at'),
                                   auto_now_add=True)

    sender_deleted_at = models.DateTimeField(_('sender deleted at'),
                                             null=True,
                                             blank=True)

    objects = MessageManager()

    class Meta:
        ordering = ['-sent_at']
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        app_label = 'discussions'

    def __str__(self):
        """ Human representation, displaying first ten words of the body. """
        from ..compat import truncate_words

        truncated_body = truncate_words(self.body, 10)
        return "%(truncated_body)s" % {'truncated_body': truncated_body}


@python_2_unicode_compatible
class Folder(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))

    created_at = models.DateTimeField(_('created at'),
                                      auto_now_add=True)

    user = models.ForeignKey(AUTH_USER_MODEL)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('folder')
        verbose_name_plural = _('folders')
        app_label = 'discussions'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('discussions_folder_detail', kwargs={
            'folder_id': self.pk
        })
