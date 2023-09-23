from datetime import datetime

from django import forms

from .models import Newsletter


class NewsletterCreateForm(forms.ModelForm):

    class Meta:
        model = Newsletter
        fields = ['time', 'finish_date', 'finish_time', 'frequency', 'clients', 'messages']
        widgets = {
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'finish_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'finish_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'clients': forms.SelectMultiple(attrs={'class': 'form-control multiselect'}),
            'messages': forms.SelectMultiple(attrs={'class': 'form-control multiselect'})
        }

    def __init__(self, *args, **kwargs):

        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['clients'].queryset = user.get_clients()
            self.fields['messages'].queryset = user.get_messages()

    def clean_finish_date(self):

        finish_date = self.cleaned_data.get('finish_date')

        if finish_date and finish_date <= datetime.now().date():
            raise forms.ValidationError("Дата завершения должна быть больше текущей даты")

        return finish_date
