from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from .models import Activity, ActivityRegistration
from .forms import ActivityForm
from django.contrib.auth.decorators import login_required
from .forms import ActivityRegistrationForm
from django.contrib.auth.decorators import user_passes_test


def activity_list(request):
    activity = Activity.objects.filter(status=Activity.Status.PUBLISHED).order_by('-published_at')
    return render(request, 'activity/activity_list.html', {'activity': activity})


def activity_detail(request, slug):
    activity = get_object_or_404(Activity, slug=slug, status=Activity.Status.PUBLISHED)
    return render(request, 'activity/activity_detail.html', {'activity': activity})

def is_organizer(user):
    return user.is_authenticated and user.groups.filter(name="ekintza-antolatzaileak").exists()

def can_create_activity(user):
    if not user.is_authenticated:
        return False
    return (
        user.groups.filter(name="ekintza-antolatzaileak").exists()
        or user.groups.filter(name="zuzendaritza-batzordea").exists()
        or user.has_perm("activity.add_activity")
    )

@login_required
@user_passes_test(can_create_activity)
def activity_create(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user

            # Si es junta y tiene permiso de publicar, puede dejarlo ya publicado (opcional)
            if request.user.has_perm("activity.can_publish_activity"):
                obj.status = Activity.Status.PUBLISHED
                obj.published_at = timezone.now()
                obj.published_by = request.user
            else:
                obj.status = Activity.Status.PENDING  # va a validación

            obj.save()
            return redirect('activity_app:activity_list')
    else:
        form = ActivityForm()
    return render(request, 'activity/activity_form.html', {'form': form})

@login_required
def activity_register(request, slug):
    activity = get_object_or_404(Activity, slug=slug, status=Activity.Status.PUBLISHED)

    if request.method == 'POST':
        form = ActivityRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.activity = activity

            # Usuario logeado (opcional)
            if request.user.is_authenticated:
                registration.user = request.user

            registration.save()
            return redirect('activity_app:activity_detail', slug=slug)
    else:
        form = ActivityRegistrationForm()

    return render(request, 'activity/activity_register.html', {
        'activity': activity,
        'form': form
    })



def activity_registered_list(request, slug):
    activity = get_object_or_404(Activity, slug=slug, status=Activity.Status.PUBLISHED)

    registrations = ActivityRegistration.objects.filter(
        activity=activity,
        anonymous=False
    ).order_by('created_at')

    return render(
        request,
        'activity/activity_registered_list.html',
        {
            'activity': activity,
            'registrations': registrations
        }
    )
