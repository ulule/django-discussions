from . import base


class Recipient(base.Recipient):
    class Meta(base.Recipient.Meta):
        abstract = False
