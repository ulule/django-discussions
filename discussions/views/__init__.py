from discussions.utils import load_class

from discussions import settings

DiscussionListView = load_class(settings.DISCUSSION_LIST_VIEW)

DiscussionSentView = load_class(settings.DISCUSSION_SENT_VIEW)

DiscussionDeletedView = load_class(settings.DISCUSSION_DELETED_VIEW)

DiscussionUnreadView = load_class(settings.DISCUSSION_UNREAD_VIEW)

DiscussionReadView = load_class(settings.DISCUSSION_READ_VIEW)

DiscussionDetailView = load_class(settings.DISCUSSION_DETAIL_VIEW)

DiscussionRemoveView = load_class(settings.DISCUSSION_REMOVE_VIEW)

DiscussionMoveView = load_class(settings.DISCUSSION_MOVE_VIEW)

DiscussionMarkAsReadView = load_class(settings.DISCUSSION_MARK_AS_READ_VIEW)

DiscussionMarkAsUnreadView = load_class(settings.DISCUSSION_MARK_AS_UNREAD_VIEW)

MessageComposeView = load_class(settings.MESSAGE_COMPOSE_VIEW)

FoldersListView = load_class(settings.FOLDER_LIST_VIEW)

FolderCreateView = load_class(settings.FOLDER_CREATE_VIEW)

FolderUpdateView = load_class(settings.FOLDER_UPDATE_VIEW)

DiscussionLeaveView = load_class(settings.DISCUSSION_LEAVE_VIEW)

FolderRemoveView = load_class(settings.FOLDER_REMOVE_VIEW)
