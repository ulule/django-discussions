from . import base

from discussions.managers import RecipientManager


class Recipient(base.Recipient):
    class Meta(base.Recipient.Meta):
        abstract = False

    objects = RecipientManager()
