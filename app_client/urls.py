from django.urls import path

from .apps import AppClientConfig
from .views import (
    ClientCreateView,
    ClientListView,
    ClientUpdateView,
    ClientDeleteView
)


app_name = AppClientConfig.name

urlpatterns = [
    path('create/', ClientCreateView.as_view(), name='client_create'),
    path('all/', ClientListView.as_view(), name='client_list'),
    path('delete/<int:pk>/', ClientDeleteView.as_view(), name='client_delete'),
    path('<int:pk>/', ClientUpdateView.as_view(), name='client_detail')
]
