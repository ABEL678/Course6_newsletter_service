import logging
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from .models import NewsletterLog, Message, Client, Newsletter

logger = logging.getLogger(__name__)


class NewsletterDeliveryService:
    """Класс, описывающий работу сервиса доставки рассылок"""

    def __init__(self, newsletter: Newsletter) -> None:
        """
        Инициализируется экземпляром класса рассылки Newsletter
        """
        self.newsletter = newsletter

    def send_mail_to_client(self):
        """
        Если время завершения периодической задачи еще не наступило,
        отправляет письма клиентам.
        """
        if self.check_task_finish_datetime():
            self.delete_task()
            return

        messages = self.newsletter.messages.all()
        clients = self.newsletter.clients.all()

        for message in messages:
            for client in clients:
                try:
                    logger.info(f'Отправка письма для {client} {client.email}')
                    send_mail(
                        subject=message.subject,
                        message=message.body,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[client.email]
                    )
                    self.save_newsletter_log(
                        status='S',
                        service_response='Письмо успешно доставлено',
                        message=message,
                        client=client
                    )
                    logger.info('Письмо отправлено')
                except Exception as error:
                    logger.error(f'Ошибка отправки письма: {error}')
                    self.save_newsletter_log(
                        status='F',
                        service_response=str(error),
                        message=message,
                        client=client
                    )

    def save_newsletter_log(self, status: str, service_response: str, message: Message, client: Client) -> None:
        """
        Сохраняет отчёт об отправке письма клиенту.
        :param status: Статус отправки письма (S - успешная отправка, F - неуспешная отправка).
        :param service_response: Ответ внешнего сервиса приёма сообщений.
        :param message: Экземпляр класса Сообщение (Message).
        :param client: Экземпляр класса Клиент (Client)
        """
        newsletter_log = NewsletterLog(
            status=status,
            server_response=service_response,
            message=message,
            client=client,
            newsletter=self.newsletter
        )
        newsletter_log.save()

    def create_schedule(self) -> CrontabSchedule:
        """
        Создаёт и возвращает расписание (CrontabSchedule) для задачи рассылки.
        В зависимости от заданной частоты рассылки (D - раз в день, W - раз в неделю,
        M - раз в месяц) и времени отправки рассылки (time) назначаются параметры
        расписания.
        """
        schedule_args = {
            'minute': self.newsletter.time.minute,
            'hour': self.newsletter.time.hour,
        }

        if self.newsletter.frequency == 'D':
            schedule_args.update(
                {
                    'day_of_week': '*',
                    'day_of_month': '*'
                }
            )

        elif self.newsletter.frequency == 'W':
            schedule_args.update(
                {
                    'day_of_week': self.newsletter.created_at.weekday(),
                    'day_of_month': '*'
                }
            )

        elif self.newsletter.frequency == 'M':
            day_of_month = self.newsletter.created_at.day if self.newsletter.created_at.day <= 28 else 28
            schedule_args.update(
                {
                    'day_of_week': '*',
                    'day_of_month': day_of_month
                }
            )

        schedule, _ = CrontabSchedule.objects.get_or_create(**schedule_args, month_of_year='*')

        return schedule

    def create_task(self):
        """
        Создаёт периодическую задачу для рассылки.
        """
        schedule = self.create_schedule()
        PeriodicTask.objects.create(
            crontab=schedule,
            name=str(self.newsletter),
            task='app_newsletter.tasks.send_newsletter',
            args=[self.newsletter.pk]
        )

    def delete_task(self):
        """
        Удаляет периодическую задачу для рассылки.
        """
        try:
            task = PeriodicTask.objects.get(name=str(self.newsletter))
            task.delete()
            self.newsletter.status = 'F'
            self.newsletter.save()
            logger.info('Задача удалена')
        except PeriodicTask.DoesNotExist:
            logger.exception(f'Периодической задачи для {self.newsletter} не существует.')

    def check_task_finish_datetime(self) -> bool:
        """
        Проверяет пришло ли время завершения периодической задачи для рассылки
        """

        end_datetime_str = f'{self.newsletter.finish_date} {self.newsletter.finish_time}'
        end_datetime = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M:%S")
        end_datetime = timezone.make_aware(end_datetime, timezone=timezone.utc)
        logger.info(f'Время завершения задачи: {end_datetime}')

        current_time = datetime.now()
        current_time = current_time.replace(tzinfo=timezone.utc)
        logger.info(f'Текущее время: {current_time}')

        if current_time > end_datetime:
            logger.info('Время истекло. Задача должна быть удалена')
            return True
        return False


class ActiveNewsletterMixin:
    """
    Mixin, который при каждом GET-запросе проверяет, активна ли рассылка.
    Если рассылка не активна, возвращается сообщение об ошибке и
    производится переадресация на страницу с деталями рассылки.
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """
        Обрабатывает GET-запрос. Если рассылка не активна, возвращается сообщение об ошибке
        и производится переадресация на страницу с деталями рассылки.

        :param request: Объект HttpRequest
        """
        newsletter = self.get_object()
        if not newsletter.is_active:
            message = f'{newsletter} отключена!'
            messages.error(request=self.request, message=message)
            return redirect(reverse('app_newsletter:newsletter_detail', kwargs={'pk': newsletter.pk}))
        return super().get(request, *args, **kwargs)
