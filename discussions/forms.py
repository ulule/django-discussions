from django import forms
from django.utils.translation import ugettext_lazy as _

from discussions.fields import CommaSeparatedUserField
from discussions.models import Discussion


class ComposeForm(forms.Form):
    to = CommaSeparatedUserField(label=_('To'))
    subject = forms.CharField(label=_('Subject'),
                              widget=forms.TextInput(),
                              required=True)
    body = forms.CharField(label=_('Message'),
                           widget=forms.Textarea({'class': 'message'}),
                           required=True)

    def save(self, sender):
        """
        Save the message and send it out into the wide world.

        :param sender:
            The :class:`User` that sends the message.

        :param parent_msg:
            The :class:`Message` that preceded this message in the thread.

        :return: The saved :class:`Message`.

        """
        to_user_list = self.cleaned_data['to']
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']

        self.discussion = Discussion.objects.send_message(sender,
                                                          to_user_list,
                                                          subject,
                                                          body)

        return self.discussion
