from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm

from .models import CustomUser


class BaseUserForm(forms.ModelForm):

    def clean(self):

        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")

        if first_name is None or first_name.strip() == "":
            self.add_error('first_name', "Имя обязательно для заполнения")

        if last_name is None or last_name.strip() == "":
            self.add_error('last_name', "Фамилия обязательна для заполнения")


class UserRegistrationForm(UserCreationForm, BaseUserForm):

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'middle_name']

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['email'].widget = forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите ваш email'})
        self.fields['first_name'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите ваше имя'})
        self.fields['last_name'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите вашу фамилию'})
        self.fields['middle_name'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите ваше отчество'})

        self.fields['password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Введите ваш пароль'})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Повторите ваш пароль'})


class UserLoginForm(AuthenticationForm):

    username = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}))

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите ваш email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите ваш пароль'
        })


class UserUpdateForm(BaseUserForm, forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'middle_name']

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите ваше имя'})
        self.fields['last_name'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите вашу фамилию'})
        self.fields['middle_name'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите ваше отчество'})


class CustomPasswordResetForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['email'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите вашу электронную почту'})


class CustomSetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите новый пароль'})
        self.fields['new_password2'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Подтвердите новый пароль'})
