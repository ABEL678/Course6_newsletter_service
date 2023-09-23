import logging

from django.conf import settings
from django.core.cache import cache

from app_client.models import Client
from app_newsletter.models import Newsletter

logger = logging.getLogger(__name__)


class MainPageDataCachingServices:

    @staticmethod
    def get_total_newsletter() -> int:

        if settings.CACHE_ENABLED:
            logger.debug('Пробую получить данные из кеша')
            total_newsletter = cache.get('total_newsletter')
            logger.debug(f'Получил: {total_newsletter}')

            if total_newsletter is None:
                logger.debug('Кеш пустой')
                total_newsletter = Newsletter.objects.count()
                cache.set('total_newsletter', total_newsletter, 10)
                logger.debug('Записал данные в кеш')

            return total_newsletter

        return Newsletter.objects.count()

    @staticmethod
    def get_active_newsletters() -> int:

        if settings.CACHE_ENABLED:
            active_newsletters = cache.get('active_newsletters')

            if active_newsletters is None:
                active_newsletters = Newsletter.objects.filter(is_active=True).count()
                cache.set('active_newsletters', active_newsletters, 120)

            return active_newsletters

        return Newsletter.objects.filter(is_active=True).count()

    @staticmethod
    def get_unique_clients() -> int:

        if settings.CACHE_ENABLED:
            unique_clients = cache.get('unique_clients')

            if unique_clients is None:
                unique_clients = Client.objects.values('email').distinct().count()
                cache.set('unique_clients', unique_clients, 180)

            return unique_clients

        return Client.objects.values('email').distinct().count()
