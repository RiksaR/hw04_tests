from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)


class CommentsForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
