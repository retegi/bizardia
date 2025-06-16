from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from .models import Activity
from .forms import ActivityForm
# Create your views here.


def activity_list(request):
    activity = Activity.objects.order_by('-published_at')
    return render(request, 'activity/activity_list.html', {'activity': activity})

def activity_detail(request, pk):
    post = get_object_or_404(Activity, pk=pk)
    return render(request, 'activity/activity_detail.html', {'post': post})

def activity_create(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('activity_list')
    else:
        form = ActivityForm()
    return render(request, 'activity/activity_form.html', {'form': form})