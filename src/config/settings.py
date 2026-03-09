from pathlib import Path
import environ
from django.utils.translation import gettext_lazy as _

# ==================================================
# Base
# ==================================================
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1"],
)

SITE_ID = 1
PUBLIC = env.bool("PUBLIC", default=True)

SITE_NAME = "Bizardia"
SITE_DOMAIN = env("SITE_DOMAIN", default="localhost:8000")

# ==================================================
# Applications
# ==================================================
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # UI / helpers
    "slippers",
    "widget_tweaks",

    # Allauth UI
    "allauth_ui",

    # Auth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # Editor
    "tinymce",

    # Rosettta
    "rosetta",

    # Project apps
    "applications.home",
    "applications.partner",
    "applications.product",
    "applications.blog",
    "applications.gallery",
    "applications.activity",
    "applications.history",
    "applications.diningRoom",
    "applications.news",
    "applications.tpv",
    "applications.announcement",
]

# ==================================================
# Middleware
# ==================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "allauth.account.middleware.AccountMiddleware",
]

# ==================================================
# Authentication
# ==================================================
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "home_app:home"
LOGOUT_REDIRECT_URL = "home_app:home"

# ==================================================
# django-allauth – Signup / Login
# ==================================================
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"

ACCOUNT_UNIQUE_EMAIL = True

ACCOUNT_SIGNUP_FIELDS = [
    "username*",
    "email*",
    "first_name",
    "last_name",
    "password1*",
    "password2*",
]

ACCOUNT_LOGIN_METHODS = {"username", "email"}

# --- Email confirmation ---
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

ACCOUNT_ADAPTER = "allauth.account.adapter.DefaultAccountAdapter"

ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = LOGIN_REDIRECT_URL
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = LOGIN_REDIRECT_URL

# ==================================================
# Social login (Google)
# ==================================================
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,
        "VERIFIED_EMAIL": True,
    }
}

# ==================================================
# URLs / Templates
# ==================================================
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ==================================================
# Database
# ==================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ==================================================
# Password validation
# ==================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ==================================================
# Internationalization
# ==================================================
LANGUAGE_CODE = "eu"
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("es", _("Español")),
    ("en", _("English")),
    ("eu", _("Euskara")),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

# ==================================================
# Static & Media
# ==================================================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==================================================
# Email (Brevo / SMTP)
# ==================================================
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)

EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")

DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL",
    default="Bizardia <no-reply@localhost>",
)

SERVER_EMAIL = env(
    "SERVER_EMAIL",
    default=DEFAULT_FROM_EMAIL,
)

EMAIL_SUBJECT_PREFIX = env(
    "EMAIL_SUBJECT_PREFIX",
    default="[Bizardia] ",
)

CONTACT_FORM_RECIPIENTS = env.list(
    "CONTACT_FORM_RECIPIENTS",
    default=["retegi84@gmail.com"],
)

EMAIL_TIMEOUT = 30


SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = [
    "https://bizardia.eus",
    "https://www.bizardia.eus",
]
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=not DEBUG)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000 if not DEBUG else 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=not DEBUG)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=not DEBUG)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=not DEBUG)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=not DEBUG)
