import logging
from typing import Dict

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import (
    LoginView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.db.models import QuerySet
from django.forms import Form
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView

from permissions.user_permission import ManagerAccessMixin
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm, CustomPasswordResetForm, CustomSetPasswordForm
from .models import CustomUser
from .services import EmailConfirmationService, email_token_generator, UserManagerService

logger = logging.getLogger(__name__)


class UserRegisterView(CreateView):

    model = CustomUser
    form_class = UserRegistrationForm
    success_url = reverse_lazy('app_main:index')

    def form_valid(self, form: Form) -> HttpResponseRedirect:

        user = form.save(commit=False)
        user.is_active = False
        user.username = user.email
        user.save()

        EmailConfirmationService.send_confirmation_email(user=user, request=self.request)

        messages.success(self.request, 'Спасибо за регистрацию! Вам на почту выслано письмо с подтверждением.')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        context['header'] = 'Регистрация'
        context['action'] = 'Зарегистрироваться'
        return context


class EmailConfirmationView(View):

    def get(self, request: HttpRequest, uidb64: str, token: str) -> HttpResponseRedirect:

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.get_user_by_id(user_id=uid)

            logger.debug('Старт процедуры подтверждения email')
            logger.debug(f"Получено из URL user.id = {user.pk}, {user}")
            logger.debug(f"Получено из URL token: {token}")

            if email_token_generator.check_token(user=user, token=token):
                logger.debug('Получен корректный токен')
                user.email_verified = True
                user.is_active = True
                user.save()
                login(request=request, user=user)
                messages.success(request=self.request, message='Регистрация на сайте успешно завершена!')
                return redirect(to='app_user:profile')

            else:
                logger.debug('Получен некорректный токен')
                messages.error(
                    request=self.request,
                    message='Ваш email не подтверждён! '
                            'Пожалуйста, проверьте вашу почту и следуйте инструкциям '
                            'для подтверждения электронной почты.'
                )
                return redirect(to='app_main:index')
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            messages.error(
                request=self.request,
                message='Ваш email не подтверждён! '
                        'Пожалуйста, проверьте вашу почту и следуйте инструкциям '
                        'для подтверждения электронной почты.'
            )
            return redirect(to='app_main:index')


class UserLoginView(LoginView):

    form_class = UserLoginForm
    template_name = 'app_user/login.html'

    def form_invalid(self, form: UserLoginForm) -> HttpResponse:

        email = form.data.get('username')

        try:
            user = CustomUser.get_user_by_email(user_email=email)

            if not user.email_verified:
                logger.debug('Попытка логина с неподтверждённой почтой')
                message = 'Ваш email не подтвержден. ' \
                          'Пожалуйста, перейдите по ссылке, отправленной на вашу электронную почту!'
                messages.error(self.request, message=message)
                return redirect(to='app_user:login')

            elif not user.is_active:
                logger.debug('Попытка логина неактивного пользователя')
                message = 'Вы заблокированы! Обратитесь к менеджеру или администратору.'
                messages.error(self.request, message=message)
                return redirect(to='app_main:index')

        except CustomUser.DoesNotExist:
            logger.debug(f'Пользователь с почтой {form.data.get("username")} не найден')
            message = 'Пользователь с таким адресом электронной почты не найден! ' \
                      'Введите корректный адрес электронной почты или ' \
                      'пройдите регистрацию на нашем сайте, если вы здесь впервые.'
            messages.error(self.request, message=message)
            return redirect(to='app_user:login')

        if form.errors.get('__all__'):
            message = 'Вы ввели неверный пароль!'
            messages.error(self.request, message=message)
            return super().form_invalid(form)

        return super().form_invalid(form)

    def get_success_url(self) -> HttpResponseRedirect:

        return reverse('app_user:profile')


def logout_user(request: HttpRequest) -> HttpResponseRedirect:

    logout(request)
    return redirect(to='app_user:login')


class ProfileUpdateView(UpdateView):

    model = CustomUser
    form_class = UserUpdateForm
    success_url = reverse_lazy('app_user:profile')

    def get_object(self, queryset=None):

        return self.request.user

    def form_valid(self, form):

        super().form_valid(form)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['title'] = f'Профиль | {self.request.user}'
        context['header'] = self.request.user
        context['action'] = 'Сохранить'
        return context


class UserListView(ManagerAccessMixin, ListView):

    model = CustomUser
    paginate_by = 5

    def get_queryset(self) -> QuerySet[CustomUser]:

        queryset = super().get_queryset()
        return queryset.exclude(is_superuser=True)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:

        user_ids_to_block = [int(user_id) for user_id in request.POST.getlist('box_active')]
        logger.info(f'User to block: {user_ids_to_block}')

        UserManagerService.unblock_all_users()
        UserManagerService.block_users(user_ids=user_ids_to_block)

        if request.user.is_superuser:
            user_ids_to_set_as_manager = [int(user_id) for user_id in request.POST.getlist('box_manager')]
            logger.info(f'User to set as manager: {user_ids_to_set_as_manager}')

            UserManagerService.remove_manager_status_all_users()
            UserManagerService.set_as_manager(user_ids=user_ids_to_set_as_manager)

        messages.success(self.request, message='Изменения сохранены')

        return redirect(self.request.path)

    def get_context_data(self, **kwargs) -> Dict[str, str]:

        context = super().get_context_data(**kwargs)
        context['title'] = 'Пользователи сервиса'
        context['header'] = 'Список пользователей'
        return context


class CustomPasswordResetView(PasswordResetView):

    email_template_name = 'app_user/password_reset_email.html'
    template_name = 'app_user/password_reset_form.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('app_user:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):

    template_name = 'app_user/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):

    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("app_user:password_reset_complete")
    template_name = "app_user/password_reset_confirm.html"


class CustomPasswordResetCompleteView(PasswordResetCompleteView):

    template_name = 'app_user/password_reset_complete.html'
