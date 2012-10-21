from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from discussions import views


urlpatterns = patterns(
    '',
    url(r'^compose(?:\/(?P<recipients>[\+\.\w]+))?/$',
        login_required(views.MessageComposeView.as_view()),
        name='discussions_compose'),

    url(r'^view/(?P<discussion_id>[\d]+)/$',
        login_required(views.DiscussionDetailView.as_view()),
        name='discussions_detail'),

    url(r'^remove/$',
        login_required(views.DiscussionRemoveView.as_view()),
        name='discussions_remove'),

    url(r'^unremove/$',
        login_required(views.DiscussionRemoveView.as_view()),
        {'undo': True},
        name='discussions_unremove'),

    url(r'^(?:(?P<username>[\.\w]+))?$',
        login_required(views.DiscussionListView.as_view()),
        name='discussions_list'),

    url(r'^sent/$',
        login_required(views.DiscussionSentView.as_view()),
        name='discussions_sent'),

    url(r'^trash/$',
        login_required(views.DiscussionDeletedView.as_view()),
        name='discussions_deleted'),

    url(r'^move/(?P<folder_id>[\d]+)$',
        login_required(views.DiscussionMoveView.as_view()),
        name='discussions_move'),

    url(r'^read/$',
        login_required(views.DiscussionReadView.as_view()),
        name='discussions_read'),

    url(r'^folder/(?P<folder_id>[\d]+)$',
        login_required(views.FolderDetailView.as_view()),
        name='discussions_folder_detail'),

    url(r'^folder/update/(?P<folder_id>[\d]+)$',
        login_required(views.FolderUpdateView.as_view()),
        name='discussions_folder_update'),

    url(r'^folder/create/$',
        login_required(views.FolderCreateView.as_view()),
        name='discussions_folder_create'),
)
