from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import TANFUser


class TANFUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        # If one field gets autocompleted but not the other, our 'neither
        # password or both password' validation will be triggered.
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'

    class Meta(UserCreationForm):
        model = TANFUser
        fields = ('email', 'stt_code',)


class TANFUserChangeForm(UserChangeForm):

    class Meta:
        model = TANFUser
        fields = ('email', 'stt_code',)
