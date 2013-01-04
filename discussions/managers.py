from django.db import models
from django.db.models import Q
from django.db.models import signals


class ContactManager(models.Manager):
    """ Manager for the :class:`MessageContact` model """

    def get_or_create(self, from_user, to_user, discussion):
        """
        Get or create a Contact

        We override Django's :func:`get_or_create` because we want contact to
        be unique in a bi-directional manner.

        """
        created = False
        try:
            contact = self.get(Q(from_user=from_user, to_user=to_user) |
                               Q(from_user=to_user, to_user=from_user))

        except self.model.DoesNotExist:
            created = True
            contact = self.create(from_user=from_user,
                                  to_user=to_user,
                                  latest_discussion=discussion)

        return (contact, created)

    def update_contact(self, from_user, to_user, message):
        """ Get or update a contacts information """
        contact, created = self.get_or_create(from_user,
                                              to_user,
                                              message)

        # If the contact already existed, update the message
        if not created:
            contact.latest_message = message
            contact.save()
        return contact

    def get_contacts_for(self, user):
        """
        Returns the contacts for this user.

        Contacts are other users that this user has received messages
        from or send messages to.

        :param user:
            The :class:`User` which to get the contacts for.

        """
        return self.filter(Q(from_user=user) | Q(to_user=user))


class DiscussionManager(models.Manager):
    """ Manager for the :class:`Message` model. """

    def send_message(self, sender, to_user_list, subject, body):
        """
        Send a message from a user, to a user.

        :param sender:
            The :class:`User` which sends the message.

        :param to_user_list:
            A list which elements are :class:`User` to whom the message is for.

        :param message:
            String containing the message.
        :return:
            A Discussion :class:`Discussion`

        """
        discussion = self.model(sender=sender,
                                subject=subject)
        discussion.save()

        discussion.save_recipients(list(to_user_list) + [sender, ])

        # Save the recipients
        discussion.update_contacts(to_user_list)

        discussion.add_message(body)

        return discussion

    def get_conversation_between(self, from_user, to_user):
        """ Returns a conversation between two users """
        messages = self.filter(Q(sender=from_user, recipients=to_user,
                                 sender_deleted_at__isnull=True) |
                               Q(sender=to_user, recipients=from_user,
                                 messagerecipient__deleted_at__isnull=True))
        return messages


class RecipientManager(models.Manager):
    """ Manager for the :class:`MessageRecipient` model. """

    def count_unread_messages_for(self, user):
        """
        Returns the amount of unread messages for this user

        :param user:
            A Django :class:`User`

        :return:
            An integer with the amount of unread messages.

        """
        unread_total = self.filter(user=user,
                                   status=self.model.STATUS.unread).count()

        return unread_total

    def count_unread_messages_between(self, to_user, from_user):
        """
        Returns the amount of unread messages between two users

        :param to_user:
            A Django :class:`User` for who the messages are for.

        :param from_user:
            A Django :class:`User` from whom the messages originate from.

        :return:
            An integer with the amount of unread messages.

        """
        unread_total = self.filter(discussion__sender=from_user,
                                   user=to_user,
                                   status=self.model.STATUS.unread).count()

        return unread_total


class MessageManager(models.Manager):
    def contribute_to_class(self, cls, name):
        signals.post_save.connect(self.post_save, sender=cls)
        return super(MessageManager, self).contribute_to_class(cls, name)

    def post_save(self, instance, **kwargs):
        if kwargs.get('created', False):
            discussion = instance.discussion

            discussion.latest_message = instance
            discussion.save()
