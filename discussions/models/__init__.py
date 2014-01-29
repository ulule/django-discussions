from discussions.utils import load_class

from discussions import settings

Recipient = load_class(settings.RECIPIENT_MODEL)

Message = load_class(settings.MESSAGE_MODEL)

Folder = load_class(settings.FOLDER_MODEL)

Discussion = load_class(settings.DISCUSSION_MODEL)
