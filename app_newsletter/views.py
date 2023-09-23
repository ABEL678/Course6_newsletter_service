from typing import Dict, Any

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from permissions.authenticate import AuthenticatedAccessMixin
from permissions.user_permission import CreatorAccessMixin, CombinedAccessMixin, NewsletterLogAccessMixin
from .forms import NewsletterCreateForm
from .models import Newsletter, NewsletterLog
from .services import NewsletterDeliveryService, ActiveNewsletterMixin


class NewsletterCreateView(AuthenticatedAccessMixin, CreateView):

    model = Newsletter
    form_class = NewsletterCreateForm

    def get_context_data(self, **kwargs) -> Dict[str, str]:

        context = super().get_context_data(**kwargs)
        context['action'] = 'Создать'
        return context

    def get_form_kwargs(self) -> Dict[str, Any]:

        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form: NewsletterCreateForm) -> HttpResponseRedirect:

        newsletter = form.save(commit=False)

        newsletter.created_by = self.request.user
        newsletter.status = 'C'
        newsletter.save()

        form.save_m2m()

        delivery_service = NewsletterDeliveryService(newsletter=newsletter)
        delivery_service.create_task()

        newsletter.status = 'S'
        newsletter.save()

        messages.success(self.request, 'Рассылка успешно создана')
        return redirect(reverse('app_main:index'))


class NewsletterListView(AuthenticatedAccessMixin, ListView):

    model = Newsletter
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Newsletter]:

        user = self.request.user
        if user.is_superuser or user.is_staff:
            queryset = Newsletter.objects.all()
        else:
            queryset = Newsletter.objects.filter(created_by=user)

        queryset = queryset.order_by('-created_at')
        return queryset


class NewsletterDetailView(CombinedAccessMixin, DetailView):

    model = Newsletter


class NewsletterUpdateView(CreatorAccessMixin, ActiveNewsletterMixin, UpdateView):

    model = Newsletter
    form_class = NewsletterCreateForm

    def form_valid(self, form: NewsletterCreateForm) -> HttpResponseRedirect:

        newsletter = form.save()

        delivery_service = NewsletterDeliveryService(newsletter=newsletter)
        delivery_service.delete_task()
        delivery_service.create_task()
        newsletter.status = 'S'
        newsletter.save()

        messages.success(request=self.request, message='Данные рассылки отредактированы')
        return redirect(reverse('app_newsletter:newsletter_detail', kwargs={'pk': newsletter.pk}))

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        """
        Возвращает контекстные данные для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        return context


class NewsletterDeleteView(CombinedAccessMixin, ActiveNewsletterMixin, DeleteView):

    model = Newsletter
    success_url = reverse_lazy('app_newsletter:newsletter_list')

    def form_valid(self, form: NewsletterCreateForm) -> HttpResponseRedirect:

        newsletter = self.get_object()

        delivery_service = NewsletterDeliveryService(newsletter=newsletter)
        delivery_service.delete_task()

        newsletter.is_active = False
        newsletter.save()
        message = f'{newsletter} отключена'

        messages.success(self.request, message)

        return HttpResponseRedirect(self.get_success_url())


class NewsletterLogListView(AuthenticatedAccessMixin, ListView):

    model = NewsletterLog
    paginate_by = 5

    def get_queryset(self) -> QuerySet[NewsletterLog]:

        user = self.request.user
        if user.is_superuser or user.is_staff:
            queryset = NewsletterLog.objects.all()
        else:
            queryset = NewsletterLog.objects.filter(newsletter__created_by=user)

        queryset = queryset.order_by('-date_time')
        return queryset


class NewsletterLogDetailView(NewsletterLogAccessMixin, DetailView):

    model = NewsletterLog
    