from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'published', 'views_count']
    list_display_links = ['title']
