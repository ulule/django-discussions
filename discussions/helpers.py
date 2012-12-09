from collections import defaultdict

from discussions.models import Discussion

from dbutils.helpers import queryset_to_dict

from discussions.utils import get_profile_model


def lookup_discussions(recipients):
    recipients_by_ids = queryset_to_dict(recipients, key='discussion_id', singular=False)

    discussions = (Discussion.objects.filter(pk__in=recipients_by_ids.keys())
                   .select_related('sender')
                   .prefetch_related('recipients'))

    for discussion in discussions:
        if discussion.pk in recipients_by_ids:
            for recipient in recipients_by_ids[discussion.pk]:
                recipient.discussion = discussion

    return recipients


def lookup_profiles(recipients):
    user_ids = defaultdict(list)

    Profile = get_profile_model()

    for recipient in recipients:
        user_ids[recipient.user_id].append(recipient.user)
        user_ids[recipient.discussion.sender_id].append(recipient.discussion.sender)

        for user in recipient.discussion.recipients.all():
            user_ids[user.pk].append(user)

    profiles = queryset_to_dict(Profile.objects.filter(user__in=user_ids), key='user_id')

    for user_id, profile in profiles.iteritems():
        if user_id in user_ids:
            for user in user_ids[user_id]:
                profile.user = user
                user._profile_cache = profile

    return recipients
