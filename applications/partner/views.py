from django.shortcuts import render
from django.views.generic import TemplateView

class SignupPendingView(TemplateView):
    template_name = 'account/signup_pending.html'

# Create your views here.
