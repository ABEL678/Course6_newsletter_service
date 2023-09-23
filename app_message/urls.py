from django.urls import path

from .apps import AppMessageConfig
from .views import (
    MessageCreateView,
    MessageListView,
    MessageUpdateView,
    MessageDeleteView
)


app_name = AppMessageConfig.name

urlpatterns = [
    path('create/', MessageCreateView.as_view(), name='message_create'),
    path('all/', MessageListView.as_view(), name='message_list'),
    path('delete/<int:pk>/', MessageDeleteView.as_view(), name='message_delete'),
    path('<int:pk>/', MessageUpdateView.as_view(), name='message_detail')
]
