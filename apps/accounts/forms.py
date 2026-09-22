from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class QuietAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields["username"].widget.attrs.pop("autofocus", None)
        self.fields["username"].widget.attrs.update(
            {"class": "qa-text-input", "autocomplete": "username"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "qa-text-input", "autocomplete": "current-password"}
        )


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.pop("autofocus", None)
        self.fields["username"].widget.attrs.update(
            {"class": "qa-text-input", "autocomplete": "username"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "qa-text-input", "autocomplete": "new-password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "qa-text-input", "autocomplete": "new-password"}
        )


class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        label="Current password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "qa-text-input", "autocomplete": "current-password"}
        ),
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise forms.ValidationError("The password is incorrect.")
        return password
