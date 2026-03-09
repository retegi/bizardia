from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from applications.news.models import News
from applications.blog.models import Post
from applications.activity.models import Activity
from applications.history.models import History
from applications.gallery.models import Gallery
from applications.home.models import HomeContent
from applications.announcement.models import Announcement
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

class HomePageView(TemplateView):
    if settings.PUBLIC:
        template_name = 'home/index.html'
    else:
        template_name = 'home/contruction.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        is_member = self.request.user.is_authenticated and self.request.user.groups.filter(name="bazkideak").exists()
        allowed_visibilities = ["public", "members"] if is_member else ["public"]

        context['current_announcement'] = Announcement.objects.filter(
            active=True,
            start_date__lte=now,
            end_date__gte=now,
            visibility__in=allowed_visibilities,
        ).first()
        context['latest_news'] = News.objects.order_by('-published_at')[:3]  # Últimas 5 noticias
        context['latest_post'] = Post.objects.order_by('-published_at')[:3]  # Últimas 5 noticias
        context['latest_activity'] = Activity.objects.filter(
            status=Activity.Status.PUBLISHED,
            activity_date_time__gte=now
        ).order_by('activity_date_time')[:6] # Últimas 5 noticias
        context['activity_outstanding'] = Activity.objects.filter(
            outstanding=True,
            status=Activity.Status.PUBLISHED,
            activity_date_time__gte=now
        ).order_by('activity_date_time')
        context['latest_history'] = History.objects.order_by('-published_at')[:1]  # Últimas 5 noticias
        context['latest_images'] = Gallery.objects.order_by('-published_at')[:6]  # Últimas 5 noticias
        context['home_content'] = HomeContent.objects.first()
        return context

class LegalNoticeView(TemplateView):
    template_name = 'home/legal-notice.html'

class PoliticalPrivacyView(TemplateView):
    template_name = 'home/political-privacy.html'

class CookiePolicyView(TemplateView):
    template_name = 'home/cookie-policy.html'

class ContactView(TemplateView):
    template_name = 'home/contact.html'


class PrivacyPolicyView(TemplateView):
    template_name = 'home/political-privacy.html'


def contact_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')

        cuerpo = f"""
        📬 Mezu berria jaso da Bizardia.eus webgunetik:

        🧑 Izena: {nombre}
        ✉️ Emaila: {email}
        🗒️ Gaia: {asunto}

        💬 Mezua:
        {mensaje}
        """

        try:
            email_msg = EmailMessage(
                subject='Mezu berria Bizardia.eus webgunetik',
                body=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=settings.CONTACT_FORM_RECIPIENTS,
                reply_to=[email] if email else None,
            )
            sent = email_msg.send(fail_silently=False)
            messages.success(request, 'Zure mezua ongi bidali da. Eskerrik asko zure harremanarengatik!' if sent == 1 else 'Ezin izan da mezua bidali.')
        except Exception as e:
            messages.error(request, f'Mezua bidaltzean errorea gertatu da: {e}')

    return HttpResponseRedirect(f"{reverse('home_app:home')}#contact")
