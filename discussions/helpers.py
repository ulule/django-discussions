from discussions.models import Discussion

from dbutils.helpers import queryset_to_dict


def lookup_discussions(recipients):
    recipients_by_ids = queryset_to_dict(recipients, key='discussion_id', singular=False)

    discussions = (Discussion.objects.filter(pk__in=recipients_by_ids.keys())
                   .select_related('sender__profile')
                   .prefetch_related('recipients'))

    for discussion in discussions:
        if discussion.pk in recipients_by_ids:
            for recipient in recipients_by_ids[discussion.pk]:
                recipient.discussion = discussion

    return recipients
