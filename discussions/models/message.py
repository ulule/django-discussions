from . import base

from discussions.managers import MessageManager


class Message(base.Message):
    class Meta(base.Message.Meta):
        abstract = False

    objects = MessageManager()
