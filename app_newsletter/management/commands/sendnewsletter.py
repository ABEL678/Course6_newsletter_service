from django.core.management import BaseCommand, CommandError, CommandParser

from app_newsletter.models import Newsletter
from app_newsletter.services import NewsletterDeliveryService


class Command(BaseCommand):
    """
    Команда для отправки рассылок клиентам.
    Пример команды: 'python manage.py sendnewsletter 1 2'
    """
    help = 'Send newsletter to clients'

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Добавляет необходимые аргументы для команды.
        Добавляется аргумент 'newsletter_id', определяющий ID рассылки,
        которую нужно отправить. Аргумент типа int и может быть передан несколько раз.
        """
        parser.add_argument('newsletter_id', type=int, nargs='+', help='Newsletter ID')

    def handle(self, *args, **options) -> None:
        """
        Обработчик команды. Вызывается при выполнении команды 'sendnewsletter' с заданными аргументами.
        В цикле обрабатываются все переданные ID рассылок.
        Для каждого ID пытается получить объект рассылки из базы данных и вызвать сервис отправки писем.
        В случае успеха выводит сообщение о успешной отправке рассылки.
        Если рассылка с указанным ID не найдена, выбрасывает исключение CommandError с соответствующим сообщением.
        """
        for newsletter_id in options['newsletter_id']:
            try:
                newsletter = Newsletter.objects.get(pk=newsletter_id)
                delivery_service = NewsletterDeliveryService(newsletter=newsletter)
                delivery_service.send_mail_to_client()
                self.stdout.write(self.style.SUCCESS(f'Successfully sent newsletter {newsletter_id}'))
            except Newsletter.DoesNotExist:
                raise CommandError(f'Newsletter "{newsletter_id}" does not exist')
