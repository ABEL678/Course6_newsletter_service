from django.db import models

from app_user.models import CustomUser


class Post(models.Model):
    """
    Модель, описывающая пост в блоге
    """
    title = models.CharField(max_length=255, unique=True, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, blank=True, verbose_name='URL')
    content = models.TextField(verbose_name='Содержание')
    preview = models.ImageField(upload_to='posts/', verbose_name='Изображение (превью)', default='posts/default.png')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    published = models.BooleanField(verbose_name='Опубликован', default=True)
    views_count = models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')
    created_by = models.ForeignKey(CustomUser, verbose_name='Автор', on_delete=models.CASCADE, related_name='post')

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        db_table = 'posts'
        ordering = ['created_at']

    def __str__(self):
        return self.title

    def increment_view_count(self):
        """
        Увеличивает счетчик просмотров поста на 1.
        """
        self.views_count += 1
        self.save()

    def make_unpublished(self):
        """
        Помечает пост как неопубликованный.
        """
        self.published = False
        self.save()
