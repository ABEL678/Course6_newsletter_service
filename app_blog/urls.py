from django.urls import path
from django.views.decorators.cache import cache_page

from .apps import AppBlogConfig
from .views import (
    PostCreateView,
    PostDetailView,
    PostListView,
    PostUpdateView,
    PostDeleteView
)

app_name = AppBlogConfig.name

urlpatterns = [
    path('posts/', cache_page(60 * 2)(PostListView.as_view()), name='post_list'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('post/update/<slug:slug>/', PostUpdateView.as_view(), name='post_update'),
    path('post/delete/<slug:slug>/', PostDeleteView.as_view(), name='post_delete'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
]
