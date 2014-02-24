from django.conf import settings


PAGINATE_BY = getattr(settings, 'DISCUSSIONS_PAGINATE_BY', 20)

RECIPIENT_MODEL = getattr(settings,
                          'DISCUSSIONS_RECIPIENT_MODEL',
                          'discussions.models.recipient.Recipient')
DISCUSSION_MODEL = getattr(settings,
                           'DISCUSSIONS_DISCUSSION_MODEL',
                           'discussions.models.discussion.Discussion')
FOLDER_MODEL = getattr(settings,
                       'DISCUSSIONS_FOLDER_MODEL',
                       'discussions.models.folder.Folder')
MESSAGE_MODEL = getattr(settings,
                        'DISCUSSIONS_MESSAGE_MODEL',
                        'discussions.models.message.Message')

DISCUSSION_LIST_VIEW = getattr(settings,
                               'DISCUSSIONS_DISCUSSION_LIST_VIEW',
                               'discussions.views.base.DiscussionListView')
DISCUSSION_SENT_VIEW = getattr(settings,
                               'DISCUSSIONS_DISCUSSION_SENT_VIEW',
                               'discussions.views.status.DiscussionSentView')
DISCUSSION_DELETED_VIEW = getattr(settings,
                                  'DISCUSSIONS_DISCUSSION_DELETED_VIEW',
                                  'discussions.views.status.DiscussionDeletedView')
DISCUSSION_READ_VIEW = getattr(settings,
                               'DISCUSSIONS_DISCUSSION_READ_VIEW',
                               'discussions.views.status.DiscussionReadView')
DISCUSSION_UNREAD_VIEW = getattr(settings,
                                 'DISCUSSIONS_DISCUSSION_UNREAD_VIEW',
                                 'discussions.views.status.DiscussionUnreadView')
DISCUSSION_DETAIL_VIEW = getattr(settings,
                                 'DISCUSSIONS_DISCUSSION_DETAIL_VIEW',
                                 'discussions.views.base.DiscussionDetailView')
DISCUSSION_REMOVE_VIEW = getattr(settings,
                                 'DISCUSSIONS_DISCUSSION_REMOVE_VIEW',
                                 'discussions.views.base.DiscussionRemoveView')
DISCUSSION_MARK_AS_READ_VIEW = getattr(settings,
                                       'DISCUSSIONS_DISCUSSION_MARK_READ_AS_VIEW',
                                       'discussions.views.base.DiscussionMarkAsReadView')

DISCUSSION_MARK_AS_UNREAD_VIEW = getattr(settings,
                                         'DISCUSSIONS_DISCUSSION_MARK_UNREAD_AS_VIEW',
                                         'discussions.views.base.DiscussionMarkAsUnreadView')

DISCUSSION_MOVE_VIEW = getattr(settings,
                               'DISCUSSIONS_DISCUSSION_MOVE_VIEW',
                               'discussions.views.base.DiscussionMoveView')
MESSAGE_COMPOSE_VIEW = getattr(settings,
                               'DISCUSSIONS_MESSAGE_COMPOSE_VIEW',
                               'discussions.views.base.MessageComposeView')
FOLDER_LIST_VIEW = getattr(settings,
                           'DISCUSSIONS_FOLDER_LIST_VIEW',
                           'discussions.views.base.FoldersListView')
FOLDER_CREATE_VIEW = getattr(settings,
                             'DISCUSSIONS_FOLDER_CREATE_VIEW',
                             'discussions.views.base.FolderCreateView')
FOLDER_UPDATE_VIEW = getattr(settings,
                             'DISCUSSIONS_FOLDER_UPDATE_VIEW',
                             'discussions.views.base.FolderUpdateView')
FOLDER_REMOVE_VIEW = getattr(settings,
                             'DISCUSSIONS_FOLDER_REMOVE_VIEW',
                             'discussions.views.base.FolderRemoveView')
DISCUSSION_LEAVE_VIEW = getattr(settings,
                                'DISCUSSIONS_DISCUSSION_LEAVE_VIEW',
                                'discussions.views.base.DiscussionLeaveView')

COMPOSE_FORM = getattr(settings, 'DISCUSSIONS_COMPOSE_FORM', 'discussions.forms.base.ComposeForm')

REPLY_FORM = getattr(settings, 'DISCUSSIONS_REPLY_FORM', 'discussions.forms.base.ReplyForm')

FOLDER_FORM = getattr(settings, 'DISCUSSIONS_FOLDER_FORM', 'discussions.forms.base.FolderForm')

PRE_FILTER = getattr(settings, 'DISCUSSIONS_PRE_FILTER', 'django.contrib.auth.decorators.login_required')
