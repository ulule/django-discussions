from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, FormView, ListView
from django.views.generic.edit import FormMixin
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ungettext
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.db import models
from django.http import Http404

from discussions.models import Recipient, Discussion
from discussions.forms import ComposeForm, ReplyForm


class DiscussionListView(ListView):
    template_name = 'discussions/list.html'
    paginate_by = 50
    model = Recipient
    context_object_name = 'discussion_list'

    def get_queryset(self):
        if self.kwargs.get('username'):
            username = self.kwargs.get('username')

            user = get_object_or_404(User, username=username)

            return (self.model.objects
                    .filter(models.Q(user=self.request.user, discussion__sender=user) |
                            models.Q(user=user, discussion__sender=self.request.user))
                    .order_by('-discussion__created_at'))

        return (self.model.objects
                .filter(user=self.request.user)
                .order_by('-discussion__created_at'))


discussion_list = login_required(DiscussionListView.as_view())


class DiscussionDetailView(DetailView, FormMixin):
    pk_url_kwarg = 'discussion_id'
    model = Discussion
    context_object_name = 'discussion'
    template_name = 'discussions/detail.html'
    form_class = ReplyForm

    def get_success_url(self):
        return reverse('discussions_detail', kwargs={
            'discussion_id': self.object.pk
        })

    def is_allowed(self, user):
        return self.object.can_view(user)

    def get_context_data(self, **kwargs):
        data = super(DiscussionDetailView, self).get_context_data(**kwargs)

        if not self.is_allowed(self.request.user):
            raise Http404

        recipients = Recipient.objects.filter(discussion=self.object,
                                              user=self.request.user,
                                              read_at__isnull=True)

        now = datetime.now()
        recipients.update(read_at=now)

        return dict(data, **{
            'recipients': recipients,
            'form': self.get_form(self.get_form_class()),
            'message_list': self.get_messages(self.object)
        })

    def get_messages(self, discussion):
        return discussion.messages.all()

    def get_template_names(self):
        return [self.template_name]

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        self.object = self.get_object()

        form.save(self.request.user)

        return super(DiscussionDetailView, self).form_valid(form)

    def get_form_kwargs(self):
        return dict(super(DiscussionDetailView, self).get_form_kwargs(), **{
            'discussion': self.get_object()
        })


discussion_detail = login_required(DiscussionDetailView.as_view())


class MessageComposeView(FormView):
    form_class = ComposeForm
    template_name = 'discussions/form.html'

    def get_template_names(self):
        return [self.template_name, ]

    def get_initial(self):
        if self.kwargs.get('recipients'):
            recipients = self.kwargs.get('recipients')

            username_list = [r.strip() for r in recipients.split('+')]
            recipients = [u for u in User.objects.filter(username__in=username_list)]

            self.recipients = recipients

            self.initial['to'] = recipients

        return self.initial

    def get_context_data(self, **kwargs):
        data = super(MessageComposeView, self).get_context_data(**kwargs)

        return dict(data, **{'recipients': self.recipients
                             if hasattr(self, 'recipients') else None})

    def form_valid(self, form):
        self.object = form.save(self.request.user)

        return redirect(self.get_success_url(form))

    def get_success_url(self, form):
        requested_redirect = self.request.REQUEST.get(REDIRECT_FIELD_NAME,
                                                      False)

        # Redirect mechanism
        redirect_to = reverse('discussions_list')
        if requested_redirect:
            redirect_to = requested_redirect
        elif self.kwargs.get('success_url'):
            redirect_to = self.kwargs.get('success_url')
        elif len(form.cleaned_data['to']) == 1:
            redirect_to = reverse('discussions_detail',
                                  kwargs={'discussion_id': self.object.pk})

        return redirect_to


message_compose = login_required(MessageComposeView.as_view())


@login_required
@require_http_methods(['POST'])
def discussion_remove(request, undo=False):
    """
    A ``POST`` to remove messages.

    :param undo:
        A Boolean that if ``True`` unremoves messages.

    POST can have the following keys:

        ``message_pks``
            List of message id's that should be deleted.

        ``next``
            String containing the URI which to redirect to after the keys are
            removed. Redirect defaults to the inbox view.

    The ``next`` value can also be supplied in the URI with ``?next=<value>``.

    """
    discussion_ids = request.POST.getlist('discussion_ids')
    redirect_to = request.REQUEST.get('next', False)

    if discussion_ids:
        # Check that all values are integers.
        valid_discussion_id_list = set()
        for pk in discussion_ids:
            try:
                valid_pk = int(pk)
            except (TypeError, ValueError):
                pass
            else:
                valid_discussion_id_list.add(valid_pk)

        # Delete all the messages, if they belong to the user.
        now = datetime.now()
        changed_message_list = set()
        for pk in valid_discussion_id_list:
            discussion = get_object_or_404(Discussion, pk=pk)

            # Check if the user is the owner
            if discussion.sender == request.user:
                if undo:
                    discussion.sender_deleted_at = None
                else:
                    discussion.sender_deleted_at = now
                discussion.save()
                changed_message_list.add(discussion.pk)

            # Check if the user is a recipient of the message
            recipients = discussion.discussionrecipient_set.filter(user=request.user,
                                                                   discussion=discussion)

            if recipients:
                for recipient in recipients:
                    recipient.mark_as_deleted()
                changed_message_list.add(discussion.pk)

        # Send messages
        if (len(changed_message_list) > 0):
            if undo:
                message = ungettext('Discussion is succesfully restored.',
                                    'Discussions are succesfully restored.',
                                    len(changed_message_list))
            else:
                message = ungettext('Discussion is successfully removed.',
                                    'Discussions are successfully removed.',
                                    len(changed_message_list))

            messages.success(request, message, fail_silently=True)

    if redirect_to:
        return redirect(redirect_to)

    return redirect(reverse('discussions_list'))
