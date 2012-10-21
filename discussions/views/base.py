from datetime import datetime

from django.views.generic import DetailView, FormView, ListView
from django.views.generic.base import View
from django.views.generic.edit import FormMixin, CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ungettext
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.db import models
from django.http import Http404

from discussions.models import Discussion, Folder, Recipient
from discussions.forms import ComposeForm, ReplyForm, FolderForm
from discussions import settings


class DiscussionListView(ListView):
    template_name = 'discussions/list.html'
    paginate_by = settings.PAGINATE_BY
    model = Recipient
    context_object_name = 'recipient_list'

    def get_queryset(self):
        if self.kwargs.get('username'):
            username = self.kwargs.get('username')

            user = get_object_or_404(User, username=username)

            qs = (self.model.objects
                  .filter(models.Q(user=self.request.user, discussion__sender=user) |
                          models.Q(user=user, discussion__sender=self.request.user)))
        else:
            qs = (self.model.objects
                  .filter(user=self.request.user))

        qs = (qs.exclude(status=self.model.STATUS.deleted)
              .exclude(folder__isnull=False)
              .order_by('-discussion__created_at')
              .select_related('discussion'))

        return qs


class DiscussionSentView(DiscussionListView):
    template_name = 'discussions/sent.html'

    def get_queryset(self):
        user = self.request.user

        qs = (self.model.objects
              .filter(discussion__sender=user, user=user))

        qs = (qs.exclude(status=self.model.STATUS.deleted)
              .order_by('-discussion__created_at')
              .select_related('discussion'))

        return qs


class DiscussionDeletedView(DiscussionListView):
    template_name = 'discussions/deleted.html'

    def get_queryset(self):
        user = self.request.user

        qs = (self.model.objects
              .filter(user=user))

        qs = (qs.filter(status=self.model.STATUS.deleted)
              .order_by('-discussion__created_at')
              .select_related('discussion'))

        return qs


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
        recipients.update(read_at=now, status=Recipient.STATUS.read)

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


class MessageComposeView(FormView):
    form_class = ComposeForm
    template_name = 'discussions/form.html'
    submit_key = 'submit'

    def get_template_names(self):
        return [self.template_name, ]

    def get_initial(self):
        recipients = None

        if self.request.method == 'POST':
            recipients = self.request.POST.get('recipients', None)
        elif self.kwargs.get('recipients'):
            recipients = self.kwargs.get('recipients')

        if recipients:
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

    def post(self, request, *args, **kwargs):
        if self.submit_key in request.POST:
            return super(MessageComposeView, self).post(request, *args, **kwargs)

        return self.get(request, *args, **kwargs)


class DiscussionBulkMixin(object):
    def valid_ids(self, ids):
        valid_discussion_id_list = set()
        for pk in ids:
            try:
                valid_pk = int(pk)
            except (TypeError, ValueError):
                pass
            else:
                valid_discussion_id_list.add(valid_pk)

        return valid_discussion_id_list


class DiscussionMoveView(DetailView, DiscussionBulkMixin):
    http_method_names = ['post']
    model = Folder
    pk_url_kwarg = 'folder_id'

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def post(self, *args, **kwargs):
        """
        A ``POST`` to move discussions into a folder.

        POST can have the following keys:

            ``discussions_ids``
                List of discussion id's that should be moved.
        """

        self.object = self.get_object()
        self.get_context_data(object=self.object)

        discussion_ids = self.request.POST.getlist('discussion_ids')

        if discussion_ids:
            Recipient.objects.filter(discussion__in=self.valid_ids(discussion_ids),
                                     user=self.request.user).update(folder=self.object)

        return redirect(reverse('discussions_list'))


class DiscussionRemoveView(View, DiscussionBulkMixin):
    http_method_names = ['post']

    def post(self, *args, **kwargs):
        """
        A ``POST`` to remove discussions.

        :param undo:
            A Boolean that if ``True`` unremoves discussions.

        POST can have the following keys:

            ``discussions_ids``
                List of discussion id's that should be deleted.

            ``next``
                String containing the URI which to redirect to after the keys are
                removed. Redirect defaults to the inbox view.

        The ``next`` value can also be supplied in the URI with ``?next=<value>``.

        """
        discussion_ids = self.request.POST.getlist('discussion_ids')
        redirect_to = self.request.REQUEST.get('next', False)
        undo = self.kwargs.get('undo', False)

        if discussion_ids:
            # Delete all the messages, if they belong to the user.
            now = datetime.now()
            changed_message_list = set()
            for pk in self.valid_ids(discussion_ids):
                discussion = get_object_or_404(Discussion, pk=pk)

                # Check if the user is the owner
                if discussion.sender == self.request.user:
                    if undo:
                        discussion.sender_deleted_at = None
                    else:
                        discussion.sender_deleted_at = now
                    discussion.save()
                    changed_message_list.add(discussion.pk)

                # Check if the user is a recipient of the message
                recipients = discussion.recipient_set.filter(user=self.request.user,
                                                             discussion=discussion)

                if recipients:
                    for recipient in recipients:
                        if undo:
                            recipient.mark_as_read()
                        else:
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

                messages.success(self.request, message, fail_silently=True)

        if redirect_to:
            return redirect(redirect_to)

        return redirect(reverse('discussions_list'))


class FolderCreateView(CreateView):
    form_class = FolderForm
    template_name = 'discussions/folder/create.html'

    def form_valid(self, form):
        self.object = form.save(self.request.user)

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('discussions_folder_detail', kwargs={
            'folder_id': self.object.pk
        })


class FolderUpdateView(UpdateView):
    form_class = FolderForm
    model = Folder
    template_name = 'discussions/folder/update.html'
    pk_url_kwarg = 'folder_id'

    def get_queryset(self):
        return self.model.objects.filter(pk=self.kwargs.get(self.pk_url_kwarg),
                                         user=self.request.user)

    def form_valid(self, form):
        self.object = form.save(self.request.user)

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('discussions_folder_update', kwargs={
            'folder_id': self.object.pk
        })


class FolderDetailView(ListView):
    model = Folder
    template_name = 'discussions/folder/detail.html'
    context_object_name = 'recipient_list'
    context_object = 'folder'
    paginate_by = settings.PAGINATE_BY

    def get_object(self):
        obj = get_object_or_404(Folder.objects.filter(user=self.request.user),
                                pk=self.kwargs.get('folder_id'))

        self.object = obj

        return obj

    def get_context_data(self, **kwargs):
        data = super(FolderDetailView, self).get_context_data(**kwargs)

        data[self.context_object] = self.object

        return data

    def get_queryset(self):
        return (self.get_object()
                .recipients
                .order_by('-discussion__created_at')
                .select_related('discussion'))
