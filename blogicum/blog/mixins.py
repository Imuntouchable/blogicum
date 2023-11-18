from blog.models import Post
from django.contrib.auth.mixins import LoginRequiredMixin


class PostMixin(LoginRequiredMixin):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
