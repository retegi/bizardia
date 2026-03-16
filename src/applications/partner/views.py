from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

from .forms import ProfileForm, UserProfileForm

class SignupPendingView(TemplateView):
    template_name = 'account/signup_pending.html'



@login_required
def partner_list(request):
    partners = Profile.objects.select_related("user").order_by("partner_number")
    return render(request, "partner/partner_list.html", {
        "partners": partners
    })


def _get_or_create_profile_for_user(user):
    profile, _created = Profile.objects.get_or_create(user=user)
    return profile


@login_required
def my_profile(request):
    profile = _get_or_create_profile_for_user(request.user)
    return render(
        request,
        "partner/my_profile.html",
        {
            "profile": profile,
        },
    )


@login_required
def my_profile_edit(request):
    profile = _get_or_create_profile_for_user(request.user)

    if request.method == "POST":
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("partner_app:my_profile")
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    return render(
        request,
        "partner/my_profile_edit.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "profile": profile,
            "page_title": _("Edit profile"),
        },
    )