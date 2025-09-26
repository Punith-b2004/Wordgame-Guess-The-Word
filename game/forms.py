from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import re
from django.core.exceptions import ValidationError

def validate_password(value):
    if len(value) < 5:
        raise ValidationError("Password must be at least 5 characters.")
    if not re.search(r'[A-Za-z]', value) or not re.search(r'\d', value) or not re.search(r'[$%@*]', value):
        raise ValidationError("Password must contain alpha, numeric, and one of $, %, *, @.")
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 5 or not re.search(r'[a-z]', username) or not re.search(r'[A-Z]', username):
            raise forms.ValidationError("Username must be at least 5 letters with both upper and lower case.")
        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 5 or not re.search(r'[a-zA-Z]', password) or not re.search(r'\d', password) or not re.search(r'[$%*@]', password):
            raise forms.ValidationError("Password must be at least 5 characters with letters, numbers, and one of $, %, *, @.")
        return password
    def validate_password(value):
        if len(value) < 5:
            raise ValidationError("Password must be at least 5 characters.")
        if not re.search(r'[A-Za-z]', value) or not re.search(r'\d', value) or not re.search(r'[$%@*]', value):
            raise ValidationError("Password must contain alpha, numeric, and one of $, %, *, @.")