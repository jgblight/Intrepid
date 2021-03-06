import datetime
import re
from django import forms
from django.forms.extras import SelectDateWidget
from django.contrib.auth.models import User


class SignupForm(forms.Form):
    username = forms.CharField(label="Username", required=True, max_length=100)
    email = forms.EmailField(label="Email", required=True)
    password1 = forms.CharField(label="Password",
                                widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Confirm Password",
                                widget=forms.PasswordInput, required=True)

    error_messages = {
        'duplicate_email': "Email already registered",
        'password_mismatch': "The two password fields didn't match",
        'invalid_email': "Not a valid email address"
    }

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()
        email = cleaned_data.get("email")
        if email:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                raise forms.ValidationError(
                    self.error_messages['invalid_email'],
                    code='invalid_email',
                )

        username = cleaned_data.get("username")
        if username:
            if User.objects.filter(username=username).count():
                raise forms.ValidationError(
                    self.error_messages['duplicate_email'],
                    code='duplicate_email',
                )

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2:
            if password1 and password2 and password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return cleaned_data


class TripForm(forms.Form):
    name = forms.CharField(
        max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Trip Title'}))
    description = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 4, 'cols': 30, 'placeholder': 'Enter a description'}), required=False)


class NewPostForm(forms.Form):
    name = forms.CharField(
        max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Post Title'}))
    loc_name = forms.CharField()
    lat = forms.FloatField(widget=forms.HiddenInput)
    lon = forms.FloatField(widget=forms.HiddenInput)
    date = forms.DateField(
        initial=datetime.date.today(), widget=forms.TextInput)


class EditProfileForm(forms.Form):
    image = forms.ImageField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    lat = forms.FloatField(widget=forms.HiddenInput, required=False)
    lon = forms.FloatField(widget=forms.HiddenInput, required=False)
    image_x = forms.FloatField(widget=forms.HiddenInput, required=False)
    image_y = forms.FloatField(widget=forms.HiddenInput, required=False)
    text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 30}), required=False)
