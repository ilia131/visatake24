
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User
from .managers import normalize_phone_number


class AdminUserCreationForm(forms.ModelForm):

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        required=False,
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model = User
        fields = (
            "phone_number",
            "role",
            "is_active",
            "is_phone_verified",
        )

    def clean_phone_number(self):
        return normalize_phone_number(
            self.cleaned_data["phone_number"]
        )

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get("password1")

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        if commit:
            user.save()

        return user


class AdminUserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = "__all__"

    def clean_password(self):
        return self.initial["password"]
