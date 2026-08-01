"""
Django settings for the Vanguard content backend.

Local dev: Postgres on localhost, media stored on disk, admin at /admin/.
"""

import os
from pathlib import Path

from django.templatetags.static import static
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-only-secret-key-change-in-production",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.import_export",
    "import_export",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "content",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "vanguard_backend.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "vanguard_backend.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "vanguard"),
        "USER": os.environ.get("POSTGRES_USER", os.environ.get("USER", "")),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# The Next.js frontend (dev) consumes the API.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3010",
    "http://127.0.0.1:3010",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-admin-token",
]

# Shared secret for Next.js admin write routes (local/dev default).
ADMIN_API_TOKEN = os.environ.get("ADMIN_API_TOKEN", "vanguard-admin-dev")

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "UNAUTHENTICATED_USER": None,
}

# ── Unfold admin theme ──────────────────────────────────────────────────────
UNFOLD = {
    "SITE_TITLE": "Vanguard Admin",
    "SITE_HEADER": "Vanguard",
    "SITE_SUBHEADER": "Website content",
    "SITE_URL": "http://localhost:3000",
    "SITE_SYMBOL": "bolt",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "THEME": "light",
    "DASHBOARD_CALLBACK": "content.dashboard.dashboard_callback",
    # CSS is also injected in templates/admin/base.html extrastyle (after Unfold).
    "STYLES": [],
    "SCRIPTS": [
        # Clears persisted dark mode from Alpine localStorage.
        lambda request: static("admin/vanguard-force-light.js"),
    ],
    "LOGIN": {
        "redirect_after": lambda request: reverse_lazy("admin:index"),
    },
    # Clean SaaS blue (matches the reference dashboard).
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
            "950": "23 37 84",
        },
    },
    "BORDER_RADIUS": "10px",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Overview",
                "separator": False,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Website content",
                "separator": True,
                "items": [
                    {
                        "title": "Services",
                        "icon": "design_services",
                        "link": reverse_lazy("admin:content_service_changelist"),
                    },
                    {
                        "title": "Projects",
                        "icon": "work",
                        "link": reverse_lazy("admin:content_project_changelist"),
                    },
                    {
                        "title": "Blog posts",
                        "icon": "article",
                        "link": reverse_lazy("admin:content_blogpost_changelist"),
                    },
                ],
            },
            {
                "title": "Footer",
                "separator": True,
                "items": [
                    {
                        "title": "Offices",
                        "icon": "location_on",
                        "link": reverse_lazy("admin:content_office_changelist"),
                    },
                    {
                        "title": "Social links",
                        "icon": "share",
                        "link": reverse_lazy("admin:content_sociallink_changelist"),
                    },
                    {
                        "title": "Footer settings",
                        "icon": "settings",
                        "link": reverse_lazy("admin:content_footersettings_changelist"),
                    },
                ],
            },
            {
                "title": "Access",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                ],
            },
        ],
    },
}
