from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Category, Location, Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_filter = ['is_published']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
