from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from .forms import PostForm, SearchForm
from django.contrib.auth.decorators import login_required

def post_list(request):
    form = SearchForm(request.GET)
    posts = Post.objects.all()
    if form.is_valid() and form.cleaned_data['query']:
        posts = posts.filter(title__icontains=form.cleaned_data['query'])
    return render(request, 'post/post_list.html', {'form': form, 'posts': posts})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'post/post_detail.html', {'post': post})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect('post_detail', slug=post.slug)
    else :
        form = PostForm()
    return render(request, 'post/post_form.html', {'form': form})

@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user:
        return redirect('post_detail', slug=post.slug)
    if request.method == 'POST':
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)

    return render(request, 'post/post_form.html', {'form': form})

@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        post.delete()
        return redirect('post_list')
    return render(request, 'post/post_confirm_delete.html', {'post': post})
