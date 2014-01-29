from . import base


class Discussion(base.Discussion):
    class Meta(base.Discussion.Meta):
        abstract = False
