from __future__ import unicode_literals

from django.views.generic import DetailView, FormView, ListView
from django.views.generic.base import View
from django.views.generic.edit import FormMixin, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _, ungettext
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import Http404
from django.utils.functional import cached_property
from django.utils.timezone import now as tznow

from ..models import Discussion, Folder, Recipient
from ..forms import ComposeForm, ReplyForm, FolderForm
from ..helpers import lookup_discussions, lookup_profiles
from .. import settings
from ..compat import User

from pure_pagination.paginator import Paginator


class DiscussionListView(ListView):
    template_name = 'discussions/list.html'
    paginate_by = settings.PAGINATE_BY
    model = Recipient
    context_object_name = 'recipient_list'
    paginator_class = Paginator

    @cached_property
    def user(self):
        return self.request.user

    @cached_property
    def folder(self):
        folder = None

        folder_id = self.kwargs.get('folder_id')

        if folder_id:
            folder = get_object_or_404(Folder.objects.filter(user=self.user), pk=folder_id)

        return folder

    def get_base_queryset(self):
        qs = (self.model.objects
              .filter(user=self.user)
              .order_by('-discussion__updated_at', '-discussion__created_at')
              .select_related('user'))

        return qs

    def get_queryset(self):
        if self.folder:
            qs = (self.get_base_queryset()
                  .filter(folder=self.folder).exclude(status=self.model.STATUS.deleted))
        else:
            qs = (self.get_base_queryset().exclude(status=self.model.STATUS.deleted)
                  .exclude(folder__isnull=False))

        return qs

    def get_context_data(self, **kwargs):
        context = super(DiscussionListView, self).get_context_data(**kwargs)

        lookup_discussions(context[self.context_object_name])
        lookup_profiles(context[self.context_object_name])

        context['folder'] = self.folder

        return context


class FoldersListView(ListView):
    template_name = 'discussions/folder/list.html'
    paginate_by = settings.PAGINATE_BY
    model = Folder
    context_object_name = 'folder_list'
    paginator_class = Paginator

    def get_queryset(self):
        qs = (self.model.objects
              .filter(user=self.request.user)
              .select_related('user'))

        return qs


class DiscussionDetailView(DetailView, FormMixin):
    pk_url_kwarg = 'discussion_id'
    model = Discussion
    context_object_name = 'discussion'
    template_name = 'discussions/detail.html'
    form_class = ReplyForm

    def get_success_url(self):
        return self.object.get_absolute_url()

    def is_allowed(self, user):
        return self.object.can_view(user)

    def get_context_data(self, **kwargs):
        data = super(DiscussionDetailView, self).get_context_data(**kwargs)

        if not self.is_allowed(self.request.user):
            raise Http404

        self.object.mark_as_read(self.request.user)

        recipients = self.object.recipients.all()

        return dict(data, **{
            'recipient_list': recipients,
            'form': self.get_form(self.get_form_class()),
            'message_list': self.get_messages(self.object),
        })

    def get_messages(self, discussion):
        return discussion.messages.order_by('sent_at')

    def get_template_names(self):
        return [self.template_name]

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        form.save(self.request.user)

        return super(DiscussionDetailView, self).form_valid(form)

    def get_form_kwargs(self):
        return dict(super(DiscussionDetailView, self).get_form_kwargs(), **{
            'discussion': self.object
        })


class MessageComposeView(FormView):
    form_class = ComposeForm
    template_name = 'discussions/form.html'
    submit_key = 'submit'

    def get_template_names(self):
        return [self.template_name, ]

    @cached_property
    def recipients(self):
        recipients = None

        if self.request.method == 'POST':
            recipients = self.request.POST.get('recipients', None)
            if recipients is None and self.kwargs.get('recipients'):
                recipients = self.kwargs.get('recipients')
        elif self.kwargs.get('recipients'):
            recipients = self.kwargs.get('recipients')

        if recipients:
            username_list = [r.strip() for r in recipients.split('+')]
            recipients = [u for u in User.objects.filter(username__in=username_list)]

        return recipients

    def get_initial(self):
        initial = {
            'to': self.recipients
        }

        return initial.copy()

    def get_context_data(self, **kwargs):
        data = super(MessageComposeView, self).get_context_data(**kwargs)

        return dict(data, **{'recipients': self.recipients
                             if hasattr(self, 'recipients') else None})

    def form_valid(self, form):
        self.object = form.save(self.request.user)

        return redirect(self.get_success_url(form))

    def get_success_url(self, form):
        requested_redirect = self.request.POST.get(REDIRECT_FIELD_NAME,
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

        self.object = None

        if self.kwargs.get('folder_id'):
            self.object = self.get_object()
            self.get_context_data(object=self.object)

        discussion_ids = self.request.POST.getlist('discussion_ids')

        if discussion_ids:
            Recipient.objects.filter(discussion__in=self.valid_ids(discussion_ids),
                                     user=self.request.user).update(folder=self.object)

        return redirect(reverse('discussions_list'))


class DiscussionMarkAsReadView(View, DiscussionBulkMixin):
    http_method_names = ['post']

    def post(self, *args, **kwargs):
        """
        A ``POST`` to mark as read discussions.

        :param unread:
            A Boolean that if ``True`` unread discussions.

        POST can have the following keys:

            ``discussions_ids``
                List of discussion id's that should be marked as read.
        """

        discussion_ids = self.request.POST.getlist('discussion_ids')

        if discussion_ids:
            recipients = (Recipient.objects.filter(discussion__in=self.valid_ids(discussion_ids),
                                                   user=self.request.user)
                          .exclude(status=Recipient.STATUS.read))
            for recipient in recipients:
                recipient.mark_as_read()

        folder_id = self.kwargs.get('folder_id')

        if folder_id:
            return redirect(reverse('discussions_list', kwargs={'folder_id': folder_id}))

        return redirect(reverse('discussions_list'))


class DiscussionMarkAsUnreadView(View, DiscussionBulkMixin):
    http_method_names = ['post']

    def post(self, *args, **kwargs):
        """
        A ``POST`` to mark as unread discussions.

        POST can have the following keys:

            ``discussions_ids``
                List of discussion id's that should be marked as unread.
        """

        discussion_ids = self.request.POST.getlist('discussion_ids')

        if discussion_ids:
            recipients = (Recipient.objects.filter(discussion__in=self.valid_ids(discussion_ids),
                                                   user=self.request.user)
                          .exclude(status=Recipient.STATUS.unread))
            for recipient in recipients:
                recipient.mark_as_unread()

        folder_id = self.kwargs.get('folder_id')

        if folder_id:
            return redirect(reverse('discussions_list', kwargs={'folder_id': folder_id}))

        return redirect(reverse('discussions_list'))


class DiscussionLeaveView(View, DiscussionBulkMixin):
    http_method_names = ['post']

    def post(self, *args, **kwargs):
        """
        A ``POST`` to leave discussions.

        POST can have the following keys:

            ``discussions_ids``
                List of discussion id's that should be deleted.

            ``next``
                String containing the URI which to redirect to after the keys are
                removed. Redirect defaults to the inbox view.

        The ``next`` value can also be supplied in the URI with ``?next=<value>``.

        """

        discussion_ids = self.request.POST.getlist('discussion_ids')
        redirect_to = self.request.POST.get('next', False)

        if discussion_ids:
            for pk in self.valid_ids(discussion_ids):
                discussion = get_object_or_404(Discussion, pk=pk)

                result = discussion.delete_recipient(self.request.user)

                if result:
                    messages.success(self.request,
                                     _('You have successfully left the discussion "%s"') % discussion,
                                     fail_silently=True)
                else:
                    messages.error(self.request,
                                   _('You have created the discussion "%s", you cannot leave it') % discussion,
                                   fail_silently=True)

        if redirect_to:
            return redirect(redirect_to)

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
        redirect_to = self.request.POST.get('next', False)
        undo = self.kwargs.get('undo', False)

        if discussion_ids:
            # Delete all the messages, if they belong to the user.
            now = tznow()
            changed_message_list = set()
            for pk in self.valid_ids(discussion_ids):
                discussion = get_object_or_404(Discussion, pk=pk)

                # Check if the user is the owner
                if discussion.sender_id == self.request.user.pk:
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
                    message = ungettext('This discussion has been succesfully restored',
                                        'These discussions have been succesfully restored',
                                        len(changed_message_list))
                else:
                    message = ungettext('This discussion has been successfully removed',
                                        'These discussions have been successfully removed',
                                        len(changed_message_list))

                messages.success(self.request, message, fail_silently=True)

        if redirect_to:
            return redirect(redirect_to)

        folder_id = self.kwargs.get('folder_id')

        if folder_id:
            return redirect(reverse('discussions_list', kwargs={'folder_id': folder_id}))

        return redirect(reverse('discussions_list'))


class FolderCreateView(CreateView):
    form_class = FolderForm
    template_name = 'discussions/folder/create.html'

    def form_valid(self, form):
        self.object = form.save(self.request.user)

        return redirect(self.get_success_url())

    def get_success_url(self):
        message = _('Your folder has been successfully created')
        messages.success(self.request, message, fail_silently=True)
        return reverse('discussions_list')


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
        message = _('You have successfully updated this folder')
        messages.success(self.request, message, fail_silently=True)
        return reverse('discussions_list', kwargs={
            'folder_id': self.object.pk
        })


class FolderRemoveView(DeleteView):
    http_method_names = ['post']
    model = Folder
    pk_url_kwarg = 'folder_id'

    def get_success_url(self):
        return reverse('discussions_list')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
