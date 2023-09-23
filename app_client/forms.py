from django import forms

from .models import Client


class ClientCreateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'first_name', 'last_name', 'middle_name', 'comment']

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['email'].widget.attrs['placeholder'] = 'Введите электронную почту клиента'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Введите имя клиента'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Введите фамилию клиента'
        self.fields['middle_name'].widget.attrs['placeholder'] = 'Введите отчество клиента (необязательно)'
        self.fields['comment'].widget.attrs['placeholder'] = 'Комментарии (необязательно)'

    def clean_email(self) -> str:
        email = self.cleaned_data.get('email')

        if self.user:
            if Client.objects.filter(created_by=self.user, email=email).exists():
                raise forms.ValidationError("Вы уже создавали клиента с таким email")
        return email
