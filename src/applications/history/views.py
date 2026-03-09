from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, permission_required
from .models import History
from .forms import HistoryForm
# Create your views here.


def history_list(request):
    content = History.objects.order_by('published_at')
    return render(request, 'history/history_list.html', {'content': content})

def history_detail(request, pk):
    content = get_object_or_404(History, pk=pk)
    return render(request, 'history/history_detail.html', {'content': content})

@login_required
@permission_required('history.add_history', raise_exception=True)
def history_create(request):
    if request.method == 'POST':
        form = HistoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('history_list')
    else:
        form = HistoryForm()
    return render(request, 'history/history_form.html', {'form': form})
