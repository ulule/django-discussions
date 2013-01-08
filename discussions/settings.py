from django.conf import settings


PAGINATE_BY = getattr(settings, 'DISCUSSIONS_PAGINATE_BY', 20)

RECIPIENT_MODEL = getattr(settings,
                          'DISCUSSIONS_RECIPIENT_MODEL',
                          'discussions.models.base.Recipient')
DISCUSSION_MODEL = getattr(settings,
                           'DISCUSSIONS_DISCUSSION_MODEL',
                           'discussions.models.base.Discussion')
FOLDER_MODEL = getattr(settings,
                       'DISCUSSIONS_FOLDER_MODEL',
                       'discussions.models.base.Folder')
MESSAGE_MODEL = getattr(settings,
                        'DISCUSSIONS_MESSAGE_MODEL',
                        'discussions.models.base.Message')
CONTACT_MODEL = getattr(settings,
                        'DISCUSSIONS_CONTACT_MODEL',
                        'discussions.models.base.Contact')

DISCUSSION_LIST_VIEW = getattr(settings,
                               'DISCUSSIONS_DISCUSSION_LIST_VIEW',
                               'discussions.views.base.DiscussionListView')
DISCUSSION_SENT_VIEW = getattr(settings,
                               'DISCUSSIONS_DISCUSSION_SENT_VIEW',
                               'discussions.views.base.DiscussionSentView')
DISCUSSION_DELETED_VIEW = getattr(settings,
                                  'DISCUSSIONS_DISCUSSION_DELETED_VIEW',
                                  'discussions.views.base.DiscussionDeletedView')
DISCUSSION_UNREAD_VIEW = getattr(settings,
                                 'DISCUSSIONS_DISCUSSION_UNREAD_VIEW',
                                 'discussions.views.base.DiscussionUnreadView')
DISCUSSION_DETAIL_VIEW = getattr(settings,
                                 'DISCUSSIONS_DISCUSSION_DETAIL_VIEW',
                                 'discussions.views.base.DiscussionDetailView')
DISCUSSION_REMOVE_VIEW = getattr(settings,
                                 'DISCUSSIONS_DISCUSSION_REMOVE_VIEW',
                                 'discussions.views.base.DiscussionRemoveView')
DISCUSSION_READ_VIEW = getattr(settings,
                               'DISCUSSIONS_DISCUSSION_READ_VIEW',
                               'discussions.views.base.DiscussionReadView')
DISCUSSION_MOVE_VIEW = getattr(settings,
                               'DISCUSSIONS_DISCUSSION_MOVE_VIEW',
                               'discussions.views.base.DiscussionMoveView')
MESSAGE_COMPOSE_VIEW = getattr(settings,
                               'DISCUSSIONS_MESSAGE_COMPOSE_VIEW',
                               'discussions.views.base.MessageComposeView')
FOLDER_CREATE_VIEW = getattr(settings,
                             'DISCUSSIONS_FOLDER_CREATE_VIEW',
                             'discussions.views.base.FolderCreateView')
FOLDER_UPDATE_VIEW = getattr(settings,
                             'DISCUSSIONS_FOLDER_UPDATE_VIEW',
                             'discussions.views.base.FolderUpdateView')
FOLDER_DETAIL_VIEW = getattr(settings,
                             'DISCUSSIONS_FOLDER_DETAIL_VIEW',
                             'discussions.views.base.FolderDetailView')

COMPOSE_FORM = getattr(settings, 'DISCUSSIONS_COMPOSE_FORM', 'discussions.forms.base.ComposeForm')

REPLY_FORM = getattr(settings, 'DISCUSSIONS_REPLY_FORM', 'discussions.forms.base.ReplyForm')

FOLDER_FORM = getattr(settings, 'DISCUSSIONS_FOLDER_FORM', 'discussions.forms.base.FolderForm')

PRE_FILTER = getattr(settings, 'DISCUSSIONS_PRE_FILTER', 'django.contrib.auth.decorators.login_required')
