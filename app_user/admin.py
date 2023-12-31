from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpRequest

from .forms import UserRegistrationForm, UserUpdateForm
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'email_verified', 'is_active', 'is_staff']
    ordering = ('email',)

    add_form = UserRegistrationForm
    form = UserUpdateForm

    def get_readonly_fields(self, request: HttpRequest, obj: CustomUser = None) -> tuple:
        if obj:
            return self.readonly_fields + ('email',)
        return self.readonly_fields

    def get_fieldsets(self, request: HttpRequest, obj: CustomUser = None) -> tuple:
        if not obj:
            fieldsets = (
                (None, {'fields': ('email', 'password1', 'password2')}),
                ('Электронная почта', {'fields': ('email_verified',)}),
                ('Персональная информация', {'fields': ('first_name', 'last_name', 'middle_name')}),
                ('Дополнительная информация', {'fields': ('comment',)}),
            )
        else:
            fieldsets = (
                (None, {'fields': ('email',)}),
                ('Электронная почта', {'fields': ('email_verified',)}),
                ('Персональная информация', {'fields': ('first_name', 'last_name', 'middle_name')}),
                ('Дополнительная информация', {'fields': ('comment',)}),
                ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
                ('Важные даты', {'fields': ('last_login', 'date_joined')})
            )
        return fieldsets
