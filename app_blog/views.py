from typing import Dict, Optional

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView
from slugify import slugify

from permissions.authenticate import AuthenticatedAccessMixin
from permissions.user_permission import CreatorAccessMixin
from .forms import PostCreateForm
from .models import Post


class PostCreateView(AuthenticatedAccessMixin, CreateView):
    """
    Представление для создания нового поста.
    Наследуется от AuthenticatedAccessMixin и Django-класса CreateView.
    Класс AuthenticatedAccessMixin обеспечивает доступ к представлению
    только аутентифицированных пользователей.
    """
    model = Post
    form_class = PostCreateForm

    login_url = reverse_lazy('app_user:login')

    def form_valid(self, form: PostCreateForm) -> HttpResponseRedirect:
        """
        Обрабатывает действие при валидной форме.
        Если форма валидна, посту присваивается slug и автор.
        :param form: Валидная форма для создания поста.
        """
        post = form.save(commit=False)
        post.slug = slugify(post.title)
        post.created_by = self.request.user
        post.save()
        messages.success(request=self.request, message='Статья успешно создана')
        return redirect(reverse('app_blog:post_detail', kwargs={'slug': post.slug}))

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        """
        Возвращает контекстные данные для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['action'] = 'Создать'
        return context


class PostListView(ListView):
    """
    Представление для отображения списка публикаций.
    """
    model = Post
    paginate_by = 4

    def get_queryset(self) -> QuerySet[Post]:
        """
        Возвращает отфильтрованный queryset с постами,
        отсортированными по дате создания в порядке убывания.
        """
        queryset = super().get_queryset()
        queryset = queryset.filter(published=True).order_by('-created_at')
        return queryset


class PostDetailView(DetailView):
    """
    Представление для отображения деталей поста.
    """
    model = Post

    def get_object(self, queryset=None) -> Optional[Post]:
        """
        Возвращает объект поста или None, если объект не найден.
        """
        obj = super().get_object(queryset=queryset)
        obj.increment_view_count()
        return obj


class PostUpdateView(CreatorAccessMixin, UpdateView):
    """
    Представление для редактирования поста.
    Наследуется от CreatorAccessMixin и Django-класса UpdateView.
    Класс CreatorAccessMixin позволяет редактировать пост
    только его автору.
    """

    model = Post
    form_class = PostCreateForm

    def form_valid(self, form: PostCreateForm) -> HttpResponseRedirect:
        """
        Обрабатывает действие при валидной форме.
        Если форма валидна, посту присваивается slug.
        :param form: Валидная форма для создания поста.
        """
        post = form.save()
        post.slug = slugify(post.title)
        post.save()
        messages.success(request=self.request, message='Статья успешно отредактирована')
        return redirect(reverse('app_blog:post_detail', kwargs={'slug': post.slug}))

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        """
        Возвращает контекстные данные для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        return context


class PostDeleteView(CreatorAccessMixin, DeleteView):
    """
    Представление для изменения статуса поста на "не опубликован".
    Наследуется от CreatorAccessMixin и Django-класса DeleteView.
    Класс CreatorAccessMixin позволяет делать пост неопубликованным
    только его автору.
    """
    model = Post
    success_url = reverse_lazy('app_blog:post_list')

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """
        Обрабатывает POST запрос для изменения статуса поста на "не опубликован".
        :param request: HTTP-запрос.
        """
        post = self.get_object()
        post.make_unpublished()

        message = f'Статус статьи "{post.title}" изменён на "не опубликован"'
        messages.success(request, message)

        return HttpResponseRedirect(self.get_success_url())
