from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from applications.news.models import News
from applications.blog.models import Post
from applications.activity.models import Activity
from applications.history.models import History
from applications.home.models import Gallery
from django.conf import settings


class HomePageView(TemplateView):
    if settings.PUBLIC:
        template_name = 'home/index.html'
    else:
        template_name = 'home/contruction.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_news'] = News.objects.order_by('-published_at')[:3]  # Últimas 5 noticias
        context['latest_post'] = Post.objects.order_by('-published_at')[:3]  # Últimas 5 noticias
        context['latest_activity'] = Activity.objects.order_by('-published_at')[:4]  # Últimas 5 noticias
        context['latest_history'] = History.objects.order_by('-published_at')[:1]  # Últimas 5 noticias
        context['latest_images'] = Gallery.objects.order_by('-published_at')[:6]  # Últimas 5 noticias
        
        return context

class LegalNoticeView(TemplateView):
    template_name = 'home/legal-notice.html'

class PoliticalPrivacyView(TemplateView):
    template_name = 'home/political-privacy.html'

class CookiePolicyView(TemplateView):
    template_name = 'home/cookie-policy.html'

class ContactView(TemplateView):
    template_name = 'home/contact.html'