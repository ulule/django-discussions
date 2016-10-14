from . import base

from discussions.managers import DiscussionManager


class Discussion(base.Discussion):
    class Meta(base.Discussion.Meta):
        abstract = False

    objects = DiscussionManager()
