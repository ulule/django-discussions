from django import forms
from django.utils.translation import ugettext_lazy as _

from ..models import Discussion, Folder


class ComposeForm(forms.Form):
    subject = forms.CharField(label=_('Subject'),
                              widget=forms.TextInput({'class': 'discrete', 'placeholder': 'Write your title'}),
                              required=True)
    body = forms.CharField(label=_('Message'),
                           widget=forms.Textarea({'class': 'message discrete', 'placeholder': 'Write your message'}),
                           required=True)

    def save(self, sender, to_user):
        """
        Save the discussion and send it out into the wide world.

        :param sender:
            The :class:`User` that sends the message.

        :return: The saved :class:`Discussion`.

        """
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']

        self.discussion = Discussion.objects.send_message(sender,
                                                          [to_user],
                                                          subject,
                                                          body)

        return self.discussion


class ReplyForm(forms.Form):
    body = forms.CharField(label=_('Message'),
                           widget=forms.Textarea({'class': 'message discrete', 'placeholder': 'Write your message'}),
                           required=True)

    def __init__(self, *args, **kwargs):
        self.discussion = kwargs.pop('discussion')

        super(ReplyForm, self).__init__(*args, **kwargs)

    def save(self, sender):
        return self.discussion.add_message(self.cleaned_data['body'], sender)


class FolderForm(forms.ModelForm):
    class Meta:
        exclude = ('user', 'discussions', 'created_at')
        model = Folder

    def save(self, user):
        self.instance.user = user

        return super(FolderForm, self).save()
