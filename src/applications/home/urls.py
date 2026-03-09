from os import name
from django.urls import include, path
from . import views



app_name = 'home_app'

urlpatterns = [
    path('',
        views.HomePageView.as_view(),
        name='home',
    ),
    path('legal_notice/',
        views.LegalNoticeView.as_view(),
        name='legal_notice',
    ),
    path('political_privacy/',
        views.PoliticalPrivacyView.as_view(),
        name='political_privacy',
    ),
    path('cookie_policy/',
        views.CookiePolicyView.as_view(),
        name='cookie_policy',
    ),
    path("privacy-policy/", views.PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("cookie-policy/", views.CookiePolicyView.as_view(), name="cookie_policy_hyphen"),
    path("legal-notice/", views.LegalNoticeView.as_view(), name="legal_notice_hyphen"),

]
