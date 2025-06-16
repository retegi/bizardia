from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# Elimina esta redirección forzada:
# path('', lambda request: HttpResponseRedirect(f'/{settings.LANGUAGE_CODE.split("-")[0]}/')),

# Solo si usas Rosetta (está bien mantenerlo)
urlpatterns = []
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('rosetta/', include('rosetta.urls')),
    ]

# ✅ Ahora envolvemos todo en i18n_patterns
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),

    # ✅ RUTA PRINCIPAL TRADUCIBLE (esto evita que falle en /es/, /eu/, /en/)
    path('', include('applications.home.urls', namespace='home_app')),

    path('blog/', include('applications.blog.urls')),
    path('news/', include('applications.news.urls')),
    path('activity/', include('applications.activity.urls')),
    path('diningroom/', include('applications.diningRoom.urls')),
    path('warehouse/', include('applications.warehouse.urls')),

    path('accounts/', include('allauth.urls')),
)

# ✅ Archivos estáticos
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
