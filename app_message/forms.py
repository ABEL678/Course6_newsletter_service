from django import forms

from .models import Message


class MessageCreateForm(forms.ModelForm):
    """
    Форма создания нового письма для рассылки.
    """

    class Meta:
        model = Message
        fields = ['subject', 'body']

    def __init__(self, *args, **kwargs) -> None:
        """
        Инициализирует форму и добавляет CSS-классы и
        плейсхолдеры для полей формы.
        """
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['subject'].widget.attrs['placeholder'] = 'Введите тему письма'
        self.fields['body'].widget.attrs['placeholder'] = 'Введите содержание письма'
