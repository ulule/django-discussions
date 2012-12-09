from discussions import settings

from discussions.utils import load_class

ComposeForm = load_class(settings.COMPOSE_FORM)

ReplyForm = load_class(settings.REPLY_FORM)

FolderForm = load_class(settings.FOLDER_FORM)
