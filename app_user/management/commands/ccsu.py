from django.core.management import BaseCommand

from app_user.models import CustomUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = CustomUser.objects.create(
            email='abel@sky.pro',
            first_name='Aleks',
            last_name='Bel',
            is_superuser=True,
            is_staff=True,
            is_active=True
        )

        user.set_password('Friday24')
        user.save()
