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
    """
    Представление для создания нового поста.
    Наследуется от AuthenticatedAccessMixin и Django-класса CreateView.
    Класс AuthenticatedAccessMixin обеспечивает доступ к представлению
    только аутентифицированным пользователям.
    """
    model = Newsletter
    form_class = NewsletterCreateForm

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        """
        Возвращает контекстные данные для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['action'] = 'Создать'
        return context

    def get_form_kwargs(self) -> Dict[str, Any]:
        """
        Добавляет текущего пользователя в kwargs формы.
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form: NewsletterCreateForm) -> HttpResponseRedirect:
        """
        Если форма валидна, сохраняет новую рассылку без коммита, задает пользователя,
        который ее создал, и статус 'C' (создано).
        Создает задачу доставки новостей и меняет статус на 'S' (рассылка запущена).
        """
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
    """
    Представление для просмотра списка рассылок.
    Наследуется от AuthenticatedAccessMixin и Django-класса ListView.
    Класс AuthenticatedAccessMixin обеспечивает доступ к представлению
    только аутентифицированным пользователям.
    """
    model = Newsletter
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Newsletter]:
        """
        Если текущий пользователь - администратор или персонал (менеджер),
        возвращает QuerySet всех рассылок.
        Для других пользователей возвращает QuerySet рассылок, созданных этим пользователем.
        Рассылки упорядочены по дате создания в обратном порядке.
        """
        user = self.request.user
        if user.is_superuser or user.is_staff:
            queryset = Newsletter.objects.all()
        else:
            queryset = Newsletter.objects.filter(created_by=user)

        queryset = queryset.order_by('-created_at')
        return queryset


class NewsletterDetailView(CombinedAccessMixin, DetailView):
    """
    Представление для просмотра деталей рассылки.
    Наследуется от CombinedAccessMixin и Django-класса DetailView.
    Класс CombinedAccessMixin обеспечивает доступ к представлению
    только администратору, персоналу и пользователю, создавшему рассылку.
    Все остальные пользователи не могут просматривать детали рассылки.
    """
    model = Newsletter


class NewsletterUpdateView(CreatorAccessMixin, ActiveNewsletterMixin, UpdateView):
    """
    Представление для редактирования рассылки.
    Наследуется от CreatorAccessMixin, ActiveNewsletterMixin и Django-класса DetailView.
    Класс CreatorAccessMixin обеспечивает доступ к представлению
    только пользователю, создавшему рассылку.
    Класс ActiveNewsletterMixin обеспечивает доступ к представлению только, если
    рассылка является активной.
    """
    model = Newsletter
    form_class = NewsletterCreateForm

    def form_valid(self, form: NewsletterCreateForm) -> HttpResponseRedirect:
        """
        Обрабатывает действия, когда форма валидна.
        Метод сохраняет рассылку, удаляет старую задачу рассылки,
        создает новую задачу рассылки и обновляет статус рассылки на 'S'.
        После редактирования рассылки, перенаправляет на страницу с деталями рассылки.

        :param form: Форма создания рассылки, которая была проверена на валидность.
        """
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
    """
    Представление для отключения рассылки.
    Наследуется от CombinedAccessMixin, ActiveNewsletterMixin и Django-класса DeleteView.
    Класс CombinedAccessMixin обеспечивает доступ к представлению
    только пользователю, создавшему рассылку, менеджеру или администратору.
    Другие пользователи не имеют доступа к отключению рассылки.
    Класс ActiveNewsletterMixin обеспечивает доступ к представлению только, если
    рассылка является активной.
    """

    model = Newsletter
    success_url = reverse_lazy('app_newsletter:newsletter_list')

    def form_valid(self, form: NewsletterCreateForm) -> HttpResponseRedirect:
        """
        Обрабатывает действия, когда форма валидна.
        Метод отключает рассылку и удаляет связанную с ней задачу рассылки.
        После отключения рассылки, перенаправляет на страницу со списком рассылок.

        :param form: Форма создания рассылки, которая была проверена на валидность.
        """
        newsletter = self.get_object()

        delivery_service = NewsletterDeliveryService(newsletter=newsletter)
        delivery_service.delete_task()

        newsletter.is_active = False
        newsletter.save()
        message = f'{newsletter} отключена'

        messages.success(self.request, message)

        return HttpResponseRedirect(self.get_success_url())


class NewsletterLogListView(AuthenticatedAccessMixin, ListView):
    """
    Представление для просмотра списка логов рассылок.
    Наследуется от AuthenticatedAccessMixin и Django-класса ListView.
    Класс AuthenticatedAccessMixin обеспечивает доступ к представлению
    только аутентифицированным пользователям.
    """
    model = NewsletterLog
    paginate_by = 5

    def get_queryset(self) -> QuerySet[NewsletterLog]:
        """
        Если текущий пользователь - администратор или персонал (менеджер),
        возвращает QuerySet всех логов рассылок.
        Для других пользователей возвращает QuerySet логов рассылок,
        созданные этим пользователем.
        Логи рассылок упорядочены по дате и времени в обратном порядке.
        """
        user = self.request.user
        if user.is_superuser or user.is_staff:
            queryset = NewsletterLog.objects.all()
        else:
            queryset = NewsletterLog.objects.filter(newsletter__created_by=user)

        queryset = queryset.order_by('-date_time')
        return queryset


class NewsletterLogDetailView(NewsletterLogAccessMixin, DetailView):
    """
    Представление для просмотра деталей лога рассылки.
    Наследуется от NewsletterLogAccessMixin и Django-класса DetailView.
    Класс NewsletterLogAccessMixin обеспечивает доступ к представлению
    только администратору, персоналу и пользователю, создавшему рассылку.
    Все остальные пользователи не могут просматривать детали лога рассылки.
    """
    model = NewsletterLog
    