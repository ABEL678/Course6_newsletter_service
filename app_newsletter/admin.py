from django.contrib import admin

from .models import Newsletter, NewsletterLog


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['pk', 'time', 'frequency', 'status', 'created_at', 'is_active', 'created_by']

    class Media:
        js = ('js/select_all.js',)


@admin.register(NewsletterLog)
class NewsletterLogAdmin(admin.ModelAdmin):
    list_display = ['date_time', 'status']
