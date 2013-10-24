from django.conf.urls import patterns, url

from . import views, settings
from .utils import load_class

pre_filter = load_class(settings.PRE_FILTER)


urlpatterns = patterns(
    '',
    url(r'^compose(?:\/(?P<recipients>[\w\-\_\+]+))?/$',
        pre_filter(views.MessageComposeView.as_view()),
        name='discussions_compose'),

    url(r'^view/(?P<discussion_id>[\d]+)/$',
        pre_filter(views.DiscussionDetailView.as_view()),
        name='discussions_detail'),

    url(r'^remove/$',
        pre_filter(views.DiscussionRemoveView.as_view()),
        name='discussions_remove'),

    url(r'^unremove/$',
        pre_filter(views.DiscussionRemoveView.as_view()),
        {'undo': True},
        name='discussions_unremove'),

    url(r'^(?:(?P<username>[\w\-\_]+))?$',
        pre_filter(views.DiscussionListView.as_view()),
        name='discussions_list'),

    url(r'^sent/$',
        pre_filter(views.DiscussionSentView.as_view()),
        name='discussions_sent'),

    url(r'^unread/$',
        pre_filter(views.DiscussionUnreadView.as_view()),
        name='discussions_unread'),

    url(r'^trash/$',
        pre_filter(views.DiscussionDeletedView.as_view()),
        name='discussions_deleted'),

    url(r'^move/(?P<folder_id>[\d]+)$',
        pre_filter(views.DiscussionMoveView.as_view()),
        name='discussions_move'),

    url(r'^read/$',
        pre_filter(views.DiscussionReadView.as_view()),
        name='discussions_read'),

    url(r'^folder/(?P<folder_id>[\d]+)$',
        pre_filter(views.FolderDetailView.as_view()),
        name='discussions_folder_detail'),

    url(r'^folder/(?P<folder_id>[\d]+)/update$',
        pre_filter(views.FolderUpdateView.as_view()),
        name='discussions_folder_update'),

    url(r'^folder/create/$',
        pre_filter(views.FolderCreateView.as_view()),
        name='discussions_folder_create'),
)
