from typing import Dict, Any

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from permissions.authenticate import AuthenticatedAccessMixin
from permissions.user_permission import CreatorAccessMixin
from .forms import ClientCreateForm
from .models import Client


class ClientCreateView(AuthenticatedAccessMixin, CreateView):
    """
    Представление для создания нового клиента.
    Наследуется от AuthenticatedAccessMixin и Django-класса CreateView.
    Класс AuthenticatedAccessMixin обеспечивает доступ к представлению
    только аутентифицированных пользователей.
    """
    model = Client
    form_class = ClientCreateForm

    login_url = reverse_lazy('app_user:login')

    def get_form_kwargs(self) -> Dict[str, Any]:
        """
        Возвращает аргументы, которые будут переданы в форму.
        """
        kwargs = super(ClientCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form: ClientCreateForm) -> HttpResponseRedirect:
        """
        Обрабатывает действие при валидной форме.
        Если форма валидна, клиенту присваивается пользователь,
        который его создал.
        :param form: Валидная форма для создания клиента.
        """
        client = form.save(commit=False)

        user = self.request.user
        client.created_by = user
        client.save()

        messages.success(request=self.request, message='Клиент успешно создан')
        return redirect(reverse('app_client:client_detail', kwargs={'pk': client.pk}))

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        """
        Возвращает контекстные данные для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['action'] = 'Создать'
        return context


class ClientListView(AuthenticatedAccessMixin, ListView):
    """
    Представление для отображения списка клиентов текущего пользователя.
    Наследуется от AuthenticatedAccessMixin и Django-класса ListView.
    Класс AuthenticatedAccessMixin обеспечивает доступ к представлению
    только аутентифицированных пользователей.
    """
    model = Client
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Client]:
        """
        Возвращает queryset с клиентами,
        которые были созданы текущим пользователем.
        """
        queryset = super().get_queryset()
        user = self.request.user
        queryset = queryset.filter(created_by=user)
        return queryset


class ClientUpdateView(CreatorAccessMixin, UpdateView):
    """
    Представление для редактирования клиента.
    Наследуется от CreatorAccessMixin и Django-класса UpdateView.
    Класс CreatorAccessMixin позволяет редактировать данные клиента
    только тому пользователю, который его создал.
    """

    model = Client
    form_class = ClientCreateForm

    def form_valid(self, form: ClientCreateForm) -> HttpResponseRedirect:
        """
        Обрабатывает действие при валидной форме.
        Если форма валидна, появляется сообщение об успешном изменении данных.
        :param form: Валидная форма для создания письма.
        """
        client = form.save()
        messages.success(request=self.request, message='Данные клиента отредактированы')
        return redirect(reverse('app_client:client_detail', kwargs={'pk': client.pk}))

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        """
        Возвращает контекстные данные для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        return context


class ClientDeleteView(CreatorAccessMixin, DeleteView):
    """
    Представление для удаления клиента.
    Наследуется от CreatorAccessMixin и Django-класса DeleteView.
    Класс CreatorAccessMixin позволяет удалять клиента
    только тому пользователю, который его создал.
    """
    model = Client
    success_url = reverse_lazy('app_client:client_list')

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """
        Обрабатывает DELETE запрос для удаления клиента.
        :param request: HTTP-запрос.
        """
        client = self.get_object()

        message = f'Клиент {client} удалён'
        messages.success(request, message)

        return HttpResponseRedirect(self.get_success_url())
    