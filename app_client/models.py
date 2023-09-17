from django.db import models

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    """
    Модель, описывающая клиента для рассылки писем
    """
    email = models.EmailField(verbose_name='Электронная почта')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=100, verbose_name='Отчество', **NULLABLE)
    comment = models.TextField(verbose_name='Комментарий', **NULLABLE)
    created_by = models.ForeignKey('app_user.CustomUser', on_delete=models.CASCADE, verbose_name='Создан',
                                   related_name='clients')

    class Meta:
        db_table = 'clients'
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
