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
        login_required(views.discussion_remove),
        name='discussions_remove'),

    url(r'^unremove/$',
        login_required(views.discussion_remove),
        {'undo': True},
        name='discussions_unremove'),

    url(r'^(?:\/(?P<username>[\.\w]+))?$',
        login_required(views.DiscussionListView.as_view()),
        name='discussions_list'),

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
