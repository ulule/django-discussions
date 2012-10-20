from django.conf import settings


PAGINATE_BY = getattr(settings, 'DISCUSSIONS_PAGINATE_BY', 20)
