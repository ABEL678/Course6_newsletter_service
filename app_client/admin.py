from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['pk', 'email', 'first_name', 'last_name']
    list_display_links = ['email']
