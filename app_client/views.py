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
    model = Client
    form_class = ClientCreateForm

    login_url = reverse_lazy('app_user:login')

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super(ClientCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form: ClientCreateForm) -> HttpResponseRedirect:
        client = form.save(commit=False)

        user = self.request.user
        client.created_by = user
        client.save()

        messages.success(request=self.request, message='Клиент успешно создан')
        return redirect(reverse('app_client:client_detail', kwargs={'pk': client.pk}))

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super().get_context_data(**kwargs)
        context['action'] = 'Создать'
        return context


class ClientListView(AuthenticatedAccessMixin, ListView):
    model = Client
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Client]:
        queryset = super().get_queryset()
        user = self.request.user
        queryset = queryset.filter(created_by=user)
        return queryset


class ClientUpdateView(CreatorAccessMixin, UpdateView):
    model = Client
    form_class = ClientCreateForm

    def form_valid(self, form: ClientCreateForm) -> HttpResponseRedirect:
        client = form.save()
        messages.success(request=self.request, message='Данные клиента отредактированы')
        return redirect(reverse('app_client:client_detail', kwargs={'pk': client.pk}))

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        return context


class ClientDeleteView(CreatorAccessMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('app_client:client_list')

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        client = self.get_object()

        message = f'Клиент {client} удалён'
        messages.success(request, message)

        return HttpResponseRedirect(self.get_success_url())
    