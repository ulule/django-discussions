from . import base


class Message(base.Message):
    class Meta(base.Message.Meta):
        abstract = False
