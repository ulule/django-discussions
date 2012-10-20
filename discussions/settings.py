from django.conf import settings


PAGINATE_BY = getattr(settings, 'DISCUSSIONS_PAGINATE_BY', 20)

RECIPIENT_MODEL = getattr(settings, 'DISCUSSIONS_RECIPIENT_MODEL', 'discussions.models.base.Recipient')

DISCUSSION_MODEL = getattr(settings, 'DISCUSSIONS_DISCUSSION_MODEL', 'discussions.models.base.Discussion')

FOLDER_MODEL = getattr(settings, 'DISCUSSIONS_FOLDER_MODEL', 'discussions.models.base.Folder')

MESSAGE_MODEL = getattr(settings, 'DISCUSSIONS_MESSAGE_MODEL', 'discussions.models.base.Message')

CONTACT_MODEL = getattr(settings, 'DISCUSSIONS_CONTACT_MODEL', 'discussions.models.base.Contact')
