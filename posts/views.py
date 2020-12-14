from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from .forms import PostForm
from .models import Group, Post

User = get_user_model()


def index(request):
    post_list = Post.objects.select_related('group').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {
            'page': page,
        }
     )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'new.html', {'form': form})
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('index')


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = profile.posts.all()

    last_post = posts[0]
    count = posts.count()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'profile.html',
        {
            'page': page,
            'profile': profile,
            'posts': posts,
            'count': count,
            'paginator': paginator,
            'last_post': last_post,
        }
    )


def post_view(request, username, post_id):
    view_post = get_object_or_404(
        Post,
        id=post_id,
        author__username=username,
    )
    profile = view_post.author
    posts = profile.posts.all()
    count = posts.count()
    return render(
        request,
        'post.html',
        {
            'profile': profile,
            'count': count,
            'view_post': view_post,
        }
    )


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = author.posts.get(id=post_id)
    if not request.user.username == username:
        return redirect('post', author, post_id)
    form = PostForm(request.POST or None, instance=post)
    if not form.is_valid():
        return render(request, 'new.html', {'form': form, 'post': post})
    form.save()
    return redirect('post', author, post_id)
