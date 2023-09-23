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
    model = Message
    form_class = MessageCreateForm

    login_url = reverse_lazy('app_user:login')

    def form_valid(self, form: MessageCreateForm) -> HttpResponseRedirect:
        message = form.save(commit=False)

        user = self.request.user
        message.created_by = user
        message.save()

        messages.success(request=self.request, message='Письмо успешно создано')
        return redirect(reverse('app_message:message_detail', kwargs={'pk': message.pk}))

    def get_context_data(self, **kwargs) -> Dict[str, str]:

        context = super().get_context_data(**kwargs)
        context['action'] = 'Создать'
        return context


class MessageListView(AuthenticatedAccessMixin, ListView):

    model = Message
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Message]:
        queryset = super().get_queryset()
        user = self.request.user
        queryset = queryset.filter(created_by=user)
        return queryset


class MessageUpdateView(CreatorAccessMixin, UpdateView):
    model = Message
    form_class = MessageCreateForm

    def form_valid(self, form: MessageCreateForm) -> HttpResponseRedirect:
        message = form.save()
        messages.success(request=self.request, message='Письмо отредактировано')
        return redirect(reverse('app_message:message_detail', kwargs={'pk': message.pk}))

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        return context


class MessageDeleteView(CreatorAccessMixin, DeleteView):
    model = Message
    success_url = reverse_lazy('app_message:message_list')

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        message = self.get_object()

        message = f'Письмо {message} удалено'
        messages.success(request, message)

        return HttpResponseRedirect(self.get_success_url())
