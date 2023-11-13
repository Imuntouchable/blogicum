from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DeleteView,
    DetailView
)
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin

from blog.forms import PostForm, UserForm, CommentForm
from blog.models import Post, Category, User, Comment
from blog.constants import NAMBER_OF_POSTS_ON_INDEX


class PostsListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = NAMBER_OF_POSTS_ON_INDEX

    def get_queryset(self):
        return Post.objects.prefetch_related(
            'location',
            'category',
            'author',).filter(
                pub_date__date__lte=timezone.now(),
                is_published=True,
                category__is_published=True
        ).annotate(comment_count=Count('comment')).order_by('-pub_date')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={
                'username': self.request.user
            }
        )


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    pk_field = 'post_id'
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_object(self):
        post_obj = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        if post_obj.author != self.request.user:
            post_obj = get_object_or_404(
                Post,
                pk=self.kwargs['post_id'],
                is_published=True,
                category__is_published=True
            )
        return post_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['form'] = CommentForm()
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        context['comments'] = Comment.objects.select_related(
            'post').filter(post=post)
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    login_url = '/auth/login/'

    def dispatch(self, request, args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        post = self.get_object()
        if post.author != request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs['post_id']
            )
        return super().dispatch(request, args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs.get('post_id')})


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'


class CommentCreateView(LoginRequiredMixin, CreateView):
    object = None
    model = Comment
    form_class = CommentForm
    pk_field = 'post_id'
    pk_url_kwarg = 'post_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs.get('post_id')})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return get_object_or_404(
            Comment,
            pk=self.kwargs.get('comment_id'),
            post=post,
            author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs.get('post_id')})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_field = 'comment_id'
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        comment_obj = self.get_object()
        if comment_obj.author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs.get('post_id')})


class ProfileListView(ListView, LoginRequiredMixin):
    template_name = 'blog/profile.html'
    paginate_by = NAMBER_OF_POSTS_ON_INDEX
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )

        if self.author != self.request.user:
            return Post.objects.select_related(
                'author',
                'location',
                'category'
            ).filter(
                is_published=True,
                pub_date__lt=timezone.now(),
                category__is_published=True,
            ).order_by('-pub_date').filter(author=self.author
                                           ).annotate(
                                               comment_count=Count('comment'))

        return Post.objects.select_related(
            'category',
            'location',
            'author'
        ).filter(
            author=self.author
        ).order_by('-pub_date').annotate(comment_count=Count('comment'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        context['user'] = self.request.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:index')


class ProfilePasswordUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:index')


class CategoryListView(ListView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = NAMBER_OF_POSTS_ON_INDEX
    pk_field = 'slugname'
    pk_url_kwarg = 'slugname'
    category = None

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['slugname'],
            is_published=True
        )
        queryset = Post.objects.filter(
            category_id=self.category.pk,
            pub_date__date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).annotate(comment_count=Count('comment')).order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['slugname'],
            is_published=True,
        )
        return context
