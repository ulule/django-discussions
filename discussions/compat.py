import django


# Django 1.5+ compatibility
if django.VERSION >= (1, 5):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    update_fields = lambda instance, fields: instance.save(update_fields=fields)
else:
    from django.contrib.auth.models import User

    update_fields = lambda instance, fields: instance.save()

# Django 1.6+ compatibility
if django.VERSION >= (1, 4):
    from django.utils.text import Truncator

    def truncate_words(s, num, end_text='...'):
        truncate = end_text and ' %s' % end_text or ''
        return Truncator(s).words(num, truncate=truncate)
else:
    from django.utils.text import truncate_words

__all__ = ['User', 'truncate_words']
