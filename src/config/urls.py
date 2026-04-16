from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

from applications.partner.views import SignupPendingView
from applications.home.views import contact_view
from applications.activity.views import ActivityRegistrationListView, stripe_webhook

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('zerrenda/', ActivityRegistrationListView.as_view(), name='activity_registration_list'),
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
]

# Rosetta (solo si está instalada)
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('rosetta/', include('rosetta.urls')),
    ]

# Rutas traducibles
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),

    # Home (raíz traducible)
    path('', include(('applications.home.urls', 'home'), namespace='home_app')),

    path('blog/', include('applications.blog.urls')),
    path('news/', include('applications.news.urls')),
    path('history/', include(('applications.history.urls', 'history'), namespace='history_app')),
    path('activity/', include('applications.activity.urls')),
    path('gallery/', include('applications.gallery.urls')),
    path('announcement/', include('applications.announcement.urls')),

    path('diningroom/', include('applications.diningRoom.urls')),
    path('partner/', include('applications.partner.urls')),

    path('registro/pending/', SignupPendingView.as_view(), name='signup_pending'),

    # Allauth


    path('contact/', contact_view, name='contact'),
    path('tpv/', include('applications.tpv.urls')),

)

# Media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
