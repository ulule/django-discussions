from django.conf.urls import url

from . import views, settings
from .utils import load_class

pre_filter = load_class(settings.PRE_FILTER)


urlpatterns = [
    url(r'^compose(?:\/(?P<recipients>[\w\-\_\+]+))?/$',
        pre_filter(views.MessageComposeView.as_view()),
        name='discussions_compose'),

    url(r'^view/(?P<discussion_id>[\d]+)/$',
        pre_filter(views.DiscussionDetailView.as_view()),
        name='discussions_detail'),

    url(r'^remove/(?:(?P<folder_id>[\d]+))?$',
        pre_filter(views.DiscussionRemoveView.as_view()),
        name='discussions_remove'),

    url(r'^unremove/$',
        pre_filter(views.DiscussionRemoveView.as_view()),
        {'undo': True},
        name='discussions_unremove'),

    url(r'^(?:(?P<username>[\w\-\_]+))?(?:folder/(?P<folder_id>[\d]+))?$',
        pre_filter(views.DiscussionListView.as_view()),
        name='discussions_list'),

    url(r'^filter/sent/(?:(?P<folder_id>[\d]+))?$',
        pre_filter(views.status.DiscussionSentView.as_view()),
        name='discussions_sent'),

    url(r'^filter/unread/(?:(?P<folder_id>[\d]+))?$',
        pre_filter(views.status.DiscussionUnreadView.as_view()),
        name='discussions_unread'),

    url(r'^filter/read/(?:(?P<folder_id>[\d]+))?$',
        pre_filter(views.status.DiscussionReadView.as_view()),
        name='discussions_read'),

    url(r'^filter/trash/(?:(?P<folder_id>[\d]+))?$',
        pre_filter(views.status.DiscussionDeletedView.as_view()),
        name='discussions_deleted'),

    url(r'^leave/$',
        pre_filter(views.DiscussionLeaveView.as_view()),
        name='discussions_leave'),

    url(r'^folders/all/$',
        pre_filter(views.FoldersListView.as_view()),
        name='discussions_folders_list'),

    url(r'^move/(?:(?P<folder_id>[\d]+))?$',
        pre_filter(views.DiscussionMoveView.as_view()),
        name='discussions_move'),

    url(r'^mark/read/(?:(?P<folder_id>[\d]+))?$',
        pre_filter(views.DiscussionMarkAsReadView.as_view()),
        name='discussions_mark_as_read'),

    url(r'^mark/unread/(?:(?P<folder_id>[\d]+))?$',
        pre_filter(views.DiscussionMarkAsUnreadView.as_view()),
        name='discussions_mark_as_unread'),

    url(r'^folder/create/$',
        pre_filter(views.FolderCreateView.as_view()),
        name='discussions_folder_create'),

    url(r'^folder/(?P<folder_id>[\d]+)/update$',
        pre_filter(views.FolderUpdateView.as_view()),
        name='discussions_folder_update'),

    url(r'^folder/remove/(?P<folder_id>[\d]+)/$',
        pre_filter(views.FolderRemoveView.as_view()),
        name='discussions_folder_remove'),
]
