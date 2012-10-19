from django.conf.urls.defaults import patterns, url

from discussions import views


urlpatterns = patterns(
    '',
    url(r'^compose/$',
        views.message_compose,
        name='discussions_compose'),

    url(r'^compose/(?P<recipients>[\+\.\w]+)/$',
        views.message_compose,
        name='discussions_compose_to'),

    url(r'^reply/(?P<parent_id>[\d]+)/$',
        views.message_compose,
        name='discussions_reply'),

    url(r'^view/(?P<discussion_id>[\d]+)/$',
        views.discussion_detail,
        name='discussions_detail'),

    url(r'^remove/$',
        views.discussion_remove,
        name='discussions_remove'),

    url(r'^unremove/$',
        views.discussion_remove,
        {'undo': True},
        name='discussions_unremove'),

    url(r'^(?:\/(?P<username>[\.\w]+))?$',
        views.discussion_list,
        name='discussions_list'),
)
