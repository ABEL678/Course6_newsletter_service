from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import QuerySet

from app_client.models import Client
from .managers import CustomUserManager

NULLABLE = {'blank': True, 'null': True}


class CustomUser(AbstractUser):
    """
    Модель, описывающая пользователя сервиса рассылок.
    Наследуется от AbstractUser.
    """
    objects = CustomUserManager()

    username = None
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    middle_name = models.CharField(max_length=100, verbose_name='Отчество', **NULLABLE)
    comment = models.TextField(verbose_name='Комментарий', **NULLABLE)
    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'users'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def make_inactive(self) -> None:
        """
        Делает пользователя неактивным.
        """
        self.is_active = False
        self.save()

    @classmethod
    def get_user_by_id(cls, user_id: int) -> 'CustomUser':
        """
        Возвращает пользователя по его идентификатору.

        :param user_id: Идентификатор пользователя.
        :return: Объект пользователя с указанным идентификатором.
        """
        return cls.objects.get(id=user_id)

    @classmethod
    def get_user_by_email(cls, user_email: str) -> 'CustomUser':
        """
        Возвращает пользователя по его электронной почте.

        :param user_email: Электронная почта пользователя.
        :return: Объект пользователя с указанной электронной почтой.
        """
        return cls.objects.get(email=user_email)

    def get_clients(self) -> QuerySet[Client]:
        """
        Возвращает всех клиентов, созданных пользователем.
        :return:
        """
        return self.clients.all()

    def get_messages(self) -> QuerySet[Client]:
        """
        Возвращает все сообщения, созданные пользователем.
        :return:
        """
        return self.messages.all()
