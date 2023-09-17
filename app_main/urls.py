from django.urls import path

from .apps import AppMainConfig
from .views import (
    IndexPageView
)

app_name = AppMainConfig.name

urlpatterns = [
    path('', IndexPageView.as_view(), name='index')
]
