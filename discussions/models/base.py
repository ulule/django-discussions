from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from discussions.managers import (DiscussionManager, RecipientManager,
                                  MessageManager)

from django.utils.timezone import now as tznow

from ..utils import get_model_string

from model_utils import Choices


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


@python_2_unicode_compatible
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

    discussion = models.ForeignKey(get_model_string('Discussion'),
                                   verbose_name=_('discussion'))

    folder = models.ForeignKey(get_model_string('Folder'),
                               verbose_name=_('folder'),
                               null=True, blank=True,
                               related_name='recipients',
                               on_delete=models.SET_NULL)

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
        abstract = True

    def __str__(self):
        return (_('%(discussion)s')
                % {'discussion': self.discussion})

    def is_read(self):
        """ Returns a boolean whether the recipient has read the message """
        return self.status == self.STATUS.read

    def is_unread(self):
        """ Returns a boolean whether the recipient hasn't read the message """
        return self.status == self.STATUS.unread

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

    def mark_as_unread(self, commit=True):
        self.status = self.STATUS.unread

        if commit:
            self.save()


@python_2_unicode_compatible
class Discussion(models.Model):
    """ Private message model, from user to user(s) """
    sender = models.ForeignKey(AUTH_USER_MODEL,
                               related_name='discussions_sent',
                               verbose_name=_('sender'))

    recipients = models.ManyToManyField(AUTH_USER_MODEL,
                                        through='Recipient',
                                        related_name='discussions_received',
                                        verbose_name=_('recipients'))

    created_at = models.DateTimeField(_('created at'),
                                      auto_now_add=True)

    updated_at = models.DateTimeField(_('updated at'),
                                      null=True, blank=True)

    sender_deleted_at = models.DateTimeField(_("sender deleted at"),
                                             null=True,
                                             blank=True)

    latest_message = models.ForeignKey(get_model_string('Message'),
                                       null=True,
                                       blank=True,
                                       on_delete=models.SET_NULL,
                                       related_name='latest_discussions')

    subject = models.CharField(max_length=255)

    recipients_count = models.PositiveIntegerField(default=0,
                                                   null=True, blank=True)

    messages_count = models.PositiveIntegerField(default=0,
                                                 null=True, blank=True)

    objects = DiscussionManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('discussion')
        verbose_name_plural = _('discussions')
        permissions = (
            ('can_view', 'Can view'),
        )
        app_label = 'discussions'
        abstract = True

    def __str__(self):
        return self.subject

    def update_counters(self, commit=True):
        self.recipients_count = self.recipients.count()
        self.messages_count = self.messages.count()

        if commit:
            self.save(update_fields=('recipients_count', 'messages_count'))

    def save_recipients(self, to_user_list):
        from . import Recipient

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

    def is_recipient(self, user):
        return user.pk in self.recipients.values_list('id', flat=True)

    def mark_as_read(self, user=None):
        from discussions.models import Recipient

        recipients = self.recipients.all()

        recipients = Recipient.objects.filter(discussion_id=self.pk)

        if user:
            recipients = recipients.filter(user_id=user.pk)

        recipients.update(read_at=tznow(), status=Recipient.STATUS.read)

    def add_message(self, body, sender=None, commit=True):
        from . import Message

        if not sender:
            sender = self.sender

        m = Message(sender=sender,
                    body=body,
                    discussion=self)
        m.save()

        if not self.is_recipient(sender):
            self.save_recipients([sender, ])

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

        if (user.is_staff or user.is_superuser or self.is_recipient(user)):
            return True

        return user.has_perm('discussions.can_view')

    def delete_recipient(self, user):
        if user.pk == self.sender_id:
            return False

        self.recipients.through.objects.filter(discussion=self.pk,
                                               user=user.pk).delete()

        return True


@python_2_unicode_compatible
class Message(models.Model):
    """ Private message model, from user to user(s) """
    sender = models.ForeignKey(AUTH_USER_MODEL,
                               related_name='sent_messages',
                               verbose_name=_('sender'))

    discussion = models.ForeignKey(get_model_string('Discussion'),
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
        abstract = True

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

    user = models.ForeignKey(AUTH_USER_MODEL, related_name='discussion_folders')

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('folder')
        verbose_name_plural = _('folders')
        app_label = 'discussions'
        abstract = True

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('discussions_folder_detail', kwargs={
            'folder_id': self.pk
        })
