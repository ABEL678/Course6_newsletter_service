# Generated by Django 4.0.4 on 2023-09-17 16:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_message', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_newsletter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsletter',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='newsletters', to=settings.AUTH_USER_MODEL, verbose_name='Создана'),
        ),
        migrations.AddField(
            model_name='newsletter',
            name='messages',
            field=models.ManyToManyField(related_name='newsletters', to='app_message.message', verbose_name='Сообщения'),
        ),
    ]
