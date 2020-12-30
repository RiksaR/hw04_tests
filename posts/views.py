from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator

from .forms import PostForm, CommentsForm
from .models import Group, Post, User, Follow


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
            'paginator': paginator,
        }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {
            'group': group,
            'page': page,
            'paginator': paginator,
        }
    )


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
    author = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(author=author).count()
    following = Follow.objects.filter(user=author).count()
    follow = Follow.objects.filter(
        user=request.user.id,
        author=author.id
        ).exists()
    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'profile.html',
        {
            'page': page,
            'author': author,
            'paginator': paginator,
            'followers': followers,
            'following': following,
            'follow': follow,
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        author__username=username,
    )
    author = post.author
    comments = post.comments.all()
    form = CommentsForm()
    return render(
        request,
        'post.html',
        {
            'post': post,
            'author': author,
            'form': form,
            'comments': comments,
        }
    )


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    if not request.user.username == username:
        return redirect('post', author.username, post_id)
    post = get_object_or_404(
        Post,
        id=post_id,
        author__username=username,
    )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if not form.is_valid():
        return render(request, 'new.html', {'form': form, 'post': post})
    form.save()
    return redirect('post', author.username, post_id)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentsForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            'comments.html',
            {
                'form': form,
                'post': post,
            }
        )
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user.id)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {
            'page': page,
            'paginator': paginator
        }
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.username != username:
        Follow.objects.get_or_create(
            user_id=request.user.id,
            author_id=author.id,
        )
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    follow = get_object_or_404(
        Follow,
        author__username=username,
        user=request.user
    )
    follow.delete()
    return redirect('profile', username=username)
