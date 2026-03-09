# applications/news/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .models import News
from .forms import NewsForm

def news_list(request):

    news_queryset = News.objects.filter(published=True)

    is_member = False

    if request.user.is_authenticated:
        try:
            is_member = request.user.profile.is_member
        except:
            is_member = False

    if is_member:
        news = news_queryset
    else:
        news = news_queryset.filter(visibility="public")

    return render(request, "news/news_list.html", {"news": news})



def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug, published=True)

    if news.visibility == "members":
        if not request.user.is_authenticated or not request.user.profile.is_member:
            return redirect("account_login")

    return render(request, "news/news_detail.html", {"news": news})


@login_required
@permission_required('news.add_news', raise_exception=True)
def news_create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('news_list')
    else:
        form = NewsForm()
    return render(request, 'news/news_form.html', {'form': form})
