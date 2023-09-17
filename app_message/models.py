from django.db import models

from app_user.models import CustomUser


class Message(models.Model):
    """
    Модель, описывающая сообщение
    """
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Создан',
                                   related_name='messages')

    class Meta:
        db_table = 'messages'
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.subject
