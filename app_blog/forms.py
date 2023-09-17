from django import forms

from .models import Post


class PostCreateForm(forms.ModelForm):
    """
    Форма для создания нового поста.
    """
    class Meta:
        model = Post
        fields = ['title', 'content', 'preview']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите текст статьи'}),
            'preview': forms.ClearableFileInput(attrs={'class': 'form-control-file'})
        }
