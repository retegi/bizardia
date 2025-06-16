from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from .models import Post
from .forms import PostForm
# Create your views here.


class HomePageView(TemplateView):
    template_name = 'home/index.html'
class LegalNoticeView(TemplateView):
    template_name = 'home/legal-notice.html'

class PoliticalPrivacyView(TemplateView):
    template_name = 'home/political-privacy.html'

class CookiePolicyView(TemplateView):
    template_name = 'home/cookie-policy.html'

class ContactView(TemplateView):
    template_name = 'home/contact.html'


def blog_list(request):
    posts = Post.objects.order_by('-fecha_creacion')
    return render(request, 'blog/blog_list.html', {'posts': posts})

def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'blog/blog_detail.html', {'post': post})

def blog_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = PostForm()
    return render(request, 'blog/blog_form.html', {'form': form})
