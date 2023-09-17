from django import forms

from .models import Client


class ClientCreateForm(forms.ModelForm):
    """
    Форма создания нового клиента для рассылки писем.
    """

    class Meta:
        model = Client
        fields = ['email', 'first_name', 'last_name', 'middle_name', 'comment']

    def __init__(self, *args, **kwargs) -> None:
        """
        Инициализирует форму и добавляет CSS-классы и
        плейсхолдеры для полей формы.
        Извлекает из kwargs пользователя и использует его для валидации адреса
        электронной почты клиента.
        """
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
        """
        Проверяет, существует ли уже клиент с таким адресом электронной почты,
        который был создан текущим пользователем. Если да, поднимает ошибку валидации.
        """
        email = self.cleaned_data.get('email')

        if self.user:
            if Client.objects.filter(created_by=self.user, email=email).exists():
                raise forms.ValidationError("Вы уже создавали клиента с таким email")
        return email
