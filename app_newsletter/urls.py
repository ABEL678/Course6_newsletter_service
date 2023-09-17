from django.urls import path

from .apps import AppNewsletterConfig
from .views import (
    NewsletterListView,
    NewsletterDetailView,
    NewsletterCreateView,
    NewsletterUpdateView,
    NewsletterDeleteView,
    NewsletterLogListView,
    NewsletterLogDetailView
)

app_name = AppNewsletterConfig.name

urlpatterns = [
    path('all/', NewsletterListView.as_view(), name='newsletter_list'),
    path('create/', NewsletterCreateView.as_view(), name='newsletter_create'),
    path('update/<int:pk>/', NewsletterUpdateView.as_view(), name='newsletter_update'),
    path('delete/<int:pk>/', NewsletterDeleteView.as_view(), name='newsletter_delete'),
    path('<int:pk>/', NewsletterDetailView.as_view(), name='newsletter_detail'),
    path('newsletterlogs/', NewsletterLogListView.as_view(), name='newsletter_log_list'),
    path('newsletterlogs/<int:pk>/', NewsletterLogDetailView.as_view(), name='newsletter_log_detail'),
]
