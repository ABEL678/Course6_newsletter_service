from typing import Dict

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from permissions.authenticate import AuthenticatedAccessMixin
from permissions.user_permission import CreatorAccessMixin
from .forms import MessageCreateForm
from .models import Message


class MessageCreateView(AuthenticatedAccessMixin, CreateView):
    """
    Представление для создания нового письма.
    Наследуется от AuthenticatedAccessMixin и Django-класса CreateView.
    Класс AuthenticatedAccessMixin обеспечивает доступ к представлению
    только аутентифицированных пользователей.
    """
    model = Message
    form_class = MessageCreateForm

    login_url = reverse_lazy('app_user:login')

    def form_valid(self, form: MessageCreateForm) -> HttpResponseRedirect:
        """
        Обрабатывает действие при валидной форме.
        Если форма валидна, письму присваивается пользователь,
        который его создал.
        :param form: Валидная форма для создания клиента.
        """
        message = form.save(commit=False)

        user = self.request.user
        message.created_by = user
        message.save()

        messages.success(request=self.request, message='Письмо успешно создано')
        return redirect(reverse('app_message:message_detail', kwargs={'pk': message.pk}))

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        """
        Возвращает контекстные данные для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['action'] = 'Создать'
        return context


class MessageListView(AuthenticatedAccessMixin, ListView):
    """
    Представление для отображения списка писем текущего пользователя.
    Наследуется от AuthenticatedAccessMixin и Django-класса ListView.
    Класс AuthenticatedAccessMixin обеспечивает доступ к представлению
    только аутентифицированных пользователей.
    """
    model = Message
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Message]:
        """
        Возвращает queryset с письмами,
        которые были созданы текущим пользователем.
        """
        queryset = super().get_queryset()
        user = self.request.user
        queryset = queryset.filter(created_by=user)
        return queryset


class MessageUpdateView(CreatorAccessMixin, UpdateView):
    """
    Представление для редактирования письма.
    Наследуется от CreatorAccessMixin и Django-класса UpdateView.
    Класс CreatorAccessMixin позволяет редактировать письмо
    только тому пользователю, который его создал.
    """

    model = Message
    form_class = MessageCreateForm

    def form_valid(self, form: MessageCreateForm) -> HttpResponseRedirect:
        """
        Обрабатывает действие при валидной форме.
        Если форма валидна, появляется сообщение об успешном изменении письма.
        :param form: Валидная форма для создания письма.
        """
        message = form.save()
        messages.success(request=self.request, message='Письмо отредактировано')
        return redirect(reverse('app_message:message_detail', kwargs={'pk': message.pk}))

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        """
        Возвращает контекстные данные для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        return context


class MessageDeleteView(CreatorAccessMixin, DeleteView):
    """
    Представление для удаления письма.
    Наследуется от CreatorAccessMixin и Django-класса DeleteView.
    Класс CreatorAccessMixin позволяет удалять письмо
    только тому пользователю, который его создал.
    """
    model = Message
    success_url = reverse_lazy('app_message:message_list')

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """
        Обрабатывает DELETE запрос для удаления письма.
        :param request: HTTP-запрос.
        """
        message = self.get_object()

        message = f'Письмо {message} удалено'
        messages.success(request, message)

        return HttpResponseRedirect(self.get_success_url())
