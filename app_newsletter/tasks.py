from celery import shared_task

from .models import Newsletter
from .services import NewsletterDeliveryService


@shared_task
def send_newsletter(newsletter_id: int) -> None:

    newsletter = Newsletter.objects.get(pk=newsletter_id)
    delivery_service = NewsletterDeliveryService(newsletter=newsletter)
    delivery_service.send_mail_to_client()
    