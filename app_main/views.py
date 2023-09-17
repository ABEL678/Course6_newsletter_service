from random import sample

from django.views.generic import TemplateView

from app_blog.models import Post
from .services import MainPageDataCachingServices


class IndexPageView(TemplateView):
    template_name = 'app_main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_newsletters'] = MainPageDataCachingServices.get_total_newsletter()
        context['active_newsletters'] = MainPageDataCachingServices.get_active_newsletters()
        context['unique_clients'] = MainPageDataCachingServices.get_unique_clients()

        all_posts = list(Post.objects.all())
        context['random_blog_posts'] = sample(all_posts, min(3, len(all_posts)))

        return context
    