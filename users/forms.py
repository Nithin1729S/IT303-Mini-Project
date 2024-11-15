from django import forms
from django.contrib.auth.models import User

class FacultyChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Old Password")
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")

    def __init__(self, *args, **kwargs):
        self.user_email = kwargs.pop('user_email', None)
        super(FacultyChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        user = User.objects.get(email=self.user_email)  # Use user_email from the form initialization
        
        if not user.check_password(old_password):
            raise forms.ValidationError("Old password is incorrect.")
        return old_password


