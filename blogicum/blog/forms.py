from django import forms

from .models import Post, User, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'text': forms.Textarea({'cols': '22', 'rows': '5'}),
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ('author',)
        fields = ('first_name', 'last_name', 'username', 'email',)


class PasswordChangeForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('password',)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
