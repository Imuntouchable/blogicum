from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Category, Location, Post)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['slug']
    list_filter = ['is_published']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
