from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Profile
from django.contrib.auth.decorators import login_required

class SignupPendingView(TemplateView):
    template_name = 'account/signup_pending.html'



@login_required
def partner_list(request):
    partners = Profile.objects.select_related("user").order_by("partner_number")
    return render(request, "partner/partner_list.html", {
        "partners": partners
    })