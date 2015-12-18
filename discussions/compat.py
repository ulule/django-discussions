import django

from django.contrib.auth import get_user_model


# Django 1.6+ compatibility
if django.VERSION >= (1, 4):
    from django.utils.text import Truncator

    def truncate_words(s, num, end_text='...'):
        truncate = end_text and ' %s' % end_text or ''
        return Truncator(s).words(num, truncate=truncate)
else:
    from django.utils.text import truncate_words

User = get_user_model()

__all__ = ['User', 'truncate_words']
