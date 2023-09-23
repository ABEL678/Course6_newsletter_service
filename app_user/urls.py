from django.urls import path

from .apps import AppUserConfig
from .views import (
    UserRegisterView,
    EmailConfirmationView,
    UserLoginView,
    logout_user,
    ProfileUpdateView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
    UserListView
)

app_name = AppUserConfig.name

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('confirm-email/<str:uidb64>/<str:token>/', EmailConfirmationView.as_view(), name='confirm_email'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('user-list/', UserListView.as_view(), name='user_list'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
]
