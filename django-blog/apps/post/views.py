from django.shortcuts import render
from .models import Post, Category

# Create your views here.
def post_list(request):
    posts = Post.objects.all()
    context = {
        'posts': posts
    }
    p=Post.objects.get(pk=3)
    print(p.categories.all())
    print(Category.objects.get(slug="sport").posts.all())
    return render(request, 'post/post_list.html', context)
