from discussions.utils import load_class

from discussions import settings

DiscussionListView = load_class(settings.DISCUSSION_LIST_VIEW)

DiscussionSentView = load_class(settings.DISCUSSION_SENT_VIEW)

DiscussionDeletedView = load_class(settings.DISCUSSION_DELETED_VIEW)

DiscussionUnreadView = load_class(settings.DISCUSSION_UNREAD_VIEW)

DiscussionDetailView = load_class(settings.DISCUSSION_DETAIL_VIEW)

DiscussionRemoveView = load_class(settings.DISCUSSION_REMOVE_VIEW)

DiscussionMoveView = load_class(settings.DISCUSSION_MOVE_VIEW)

DiscussionReadView = load_class(settings.DISCUSSION_READ_VIEW)

MessageComposeView = load_class(settings.MESSAGE_COMPOSE_VIEW)

FolderCreateView = load_class(settings.FOLDER_CREATE_VIEW)

FolderUpdateView = load_class(settings.FOLDER_UPDATE_VIEW)

FolderDetailView = load_class(settings.FOLDER_DETAIL_VIEW)
