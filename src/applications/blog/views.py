from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, permission_required
from .models import Post
from .forms import PostForm
# Create your views here.


def blog_list(request):
    posts = Post.objects.order_by('-published_at')
    return render(request, 'blog/blog_list.html', {'posts': posts})

def blog_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/blog_detail.html', {'post': post})

@login_required
@permission_required('blog.add_post', raise_exception=True)
def blog_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = PostForm()
    return render(request, 'blog/blog_form.html', {'form': form})
