from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group, Follow
from .forms import PostForm, CommentForm
# Create your views here.


def index(request):
    post_list = Post.objects.select_related('group').order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=author).exists()
    return render(request, 'profile.html', {'author': author, 'page': page, 'paginator': paginator,
                                            'following': following})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    form = CommentForm()
    comments = post.comments.all()
    return render(request, 'post.html', {'author': author, 'post': post, 'form': form, 'comments': comments})


@login_required()
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user.username != username:
        return redirect('post', username=username, post_id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post', username=username, post_id=post_id)
        return redirect('new_post')
    else:
        form = PostForm(instance=post)
    return render(request, 'new_post.html', {'form': form, 'post': post})


@login_required()
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post', username=username, post_id=post_id)
        return redirect('index')
    else:
        form = CommentForm()
    return render(request, 'comments.html', {'form': form, 'post': post})


@login_required()
def follow_index(request):
    followed_authors = Follow.objects.filter(user=request.user).values_list('author_id')
    posts = Post.objects.filter(author_id__in=followed_authors)
    post_list = posts.order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page})


@login_required()
def profile_follow(request, username):
    followed = get_object_or_404(User, username=username)
    if request.user != followed and not Follow.objects.filter(user=request.user, author=followed).exists():
        Follow.objects.create(user=request.user, author=followed)
    return redirect('profile', username=username)


@login_required()
def profile_unfollow(request, username):
    followed = get_object_or_404(User, username=username)
    if request.user != followed and Follow.objects.filter(user=request.user, author=followed).exists():
        Follow.objects.filter(user=request.user, author=followed).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
