from ..utils import load_class
from .. import settings


class DiscussionSentView(load_class(settings.DISCUSSION_LIST_VIEW)):
    template_name = 'discussions/sent.html'

    def get_queryset(self):
        return (self.get_base_queryset()
                .filter(discussion__sender=self.user, folder=self.folder)
                .exclude(status=self.model.STATUS.deleted))


class DiscussionUnreadView(load_class(settings.DISCUSSION_LIST_VIEW)):
    template_name = 'discussions/unread.html'

    def get_queryset(self):
        return (self.get_base_queryset()
                .filter(status=self.model.STATUS.unread, folder=self.folder))


class DiscussionReadView(load_class(settings.DISCUSSION_LIST_VIEW)):
    template_name = 'discussions/read.html'

    def get_queryset(self):
        return (self.get_base_queryset()
                .filter(status=self.model.STATUS.read, folder=self.folder))


class DiscussionDeletedView(load_class(settings.DISCUSSION_LIST_VIEW)):
    template_name = 'discussions/deleted.html'

    def get_queryset(self):
        return (self.get_base_queryset()
                .filter(status=self.model.STATUS.deleted, folder=self.folder))
