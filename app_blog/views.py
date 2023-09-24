from typing import Dict, Optional

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView
from pytils.translit import slugify

from permissions.authenticate import AuthenticatedAccessMixin
from permissions.user_permission import CreatorAccessMixin
from .forms import PostCreateForm
from .models import Post


class PostCreateView(AuthenticatedAccessMixin, CreateView):
    model = Post
    form_class = PostCreateForm

    login_url = reverse_lazy('app_user:login')

    def form_valid(self, form: PostCreateForm) -> HttpResponseRedirect:
        post = form.save(commit=False)
        post.slug = slugify(post.title)
        post.created_by = self.request.user
        post.save()
        messages.success(request=self.request, message='Статья успешно создана')
        return redirect(reverse('app_blog:post_detail', kwargs={'slug': post.slug}))

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super().get_context_data(**kwargs)
        context['action'] = 'Создать'
        return context


class PostListView(ListView):
    model = Post
    paginate_by = 4

    def get_queryset(self) -> QuerySet[Post]:
        queryset = super().get_queryset()
        queryset = queryset.filter(published=True).order_by('-created_at')
        return queryset


class PostDetailView(DetailView):
    model = Post

    def get_object(self, queryset=None) -> Optional[Post]:
        obj = super().get_object(queryset=queryset)
        obj.increment_view_count()
        return obj


class PostUpdateView(CreatorAccessMixin, UpdateView):
    model = Post
    form_class = PostCreateForm

    def form_valid(self, form: PostCreateForm) -> HttpResponseRedirect:
        post = form.save()
        post.slug = slugify(post.title)
        post.save()
        messages.success(request=self.request, message='Статья успешно отредактирована')
        return redirect(reverse('app_blog:post_detail', kwargs={'slug': post.slug}))

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        return context


class PostDeleteView(CreatorAccessMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('app_blog:post_list')

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        post = self.get_object()
        post.make_unpublished()

        message = f'Статус статьи "{post.title}" изменён на "не опубликован"'
        messages.success(request, message)

        return HttpResponseRedirect(self.get_success_url())
