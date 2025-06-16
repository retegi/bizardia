# applications/news/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import News
from .forms import NewsForm

def news_list(request):
    news_items = News.objects.order_by('-published_at')
    return render(request, 'news/news_list.html', {'news_items': news_items})

def news_detail(request, pk):
    news = get_object_or_404(News, pk=pk)
    return render(request, 'news/news_detail.html', {'news': news})

def news_create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('news_list')
    else:
        form = NewsForm()
    return render(request, 'news/news_form.html', {'form': form})
