from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from .models import History
from .forms import HistoryForm
# Create your views here.


def history_list(request):
    posts = History.objects.order_by('-fecha_creacion')
    return render(request, 'history/history_list.html', {'posts': posts})

def history_detail(request, slug):
    post = get_object_or_404(History, slug=slug)
    return render(request, 'history/history_detail.html', {'post': post})

def history_create(request):
    if request.method == 'POST':
        form = HistoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('history_list')
    else:
        form = HistoryForm()
    return render(request, 'history/history_form.html', {'form': form})