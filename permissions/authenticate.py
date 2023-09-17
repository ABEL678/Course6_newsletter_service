from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy


class AuthenticatedAccessMixin(LoginRequiredMixin):
    """
    Миксин для проверки аутентификации пользователя.
    """
    login_url = reverse_lazy('app_user:login')

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """
        Переопределение метода dispatch для проверки аутентификации пользователя.
        Если пользователь не аутентифицирован, он будет перенаправлен на страницу входа.
        :param request: HttpRequest объект.
        """
        if not request.user.is_authenticated:
            messages.info(request, 'Необходимо авторизоваться!')
            return redirect(self.login_url)

        return super().dispatch(request, *args, **kwargs)
