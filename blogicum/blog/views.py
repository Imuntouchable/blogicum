from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blog.forms import CommentForm, PostForm, UserForm
from blog.mixins import PostMixin
from blog.models import Category, Comment, Post, User

from blog.constants import NAMBER_OF_POSTS_ON_INDEX


class PostsListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = NAMBER_OF_POSTS_ON_INDEX

    def get_queryset(self):
        return Post.objects.prefetch_related(
            'location',
            'category',
            'author',
        ).filter(
            pub_date__date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')


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


class PostDetailView(DetailView):
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
                category__is_published=True,
                pub_date__lt=timezone.now(),
            )
        return post_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']}
                            )


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    success_url = reverse_lazy('blog:index')


class CommentCreateView(LoginRequiredMixin, CreateView):
    object = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
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
        return reverse('blog:post_detail',
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
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs.get('post_id')})


class ProfileDetailView(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = NAMBER_OF_POSTS_ON_INDEX

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
                                               comment_count=Count('comments'))

        return Post.objects.select_related(
            'category',
            'location',
            'author'
        ).filter(
            author=self.author
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:index')


class ProfilePasswordUpdateView(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:index')


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = NAMBER_OF_POSTS_ON_INDEX

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
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['slugname'],
            is_published=True,
        )
        return context
