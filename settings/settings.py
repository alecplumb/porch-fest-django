from pathlib 	import Path
from decouple 	import config
import sys
import platform
import os
if os.name == 'nt':
    GDAL_LIBRARY_PATH = os.path.join(config('PROJECT_PATH'), r'porch-fest-django\venv\Lib\site-packages\osgeo\gdal.dll')
    GEOS_LIBRARY_PATH = os.path.join(config('PROJECT_PATH'), r'porch-fest-django\venv\Lib\site-packages\osgeo\geos_c.dll')
if sys.platform == 'darwin':
    if platform.machine() == 'x86_64':
        # Intel Mac, or Python running under Rosetta
        GDAL_LIBRARY_PATH = "/opt/local/lib/libgdal.dylib"
        GEOS_LIBRARY_PATH = "/opt/local/lib/libgeos_c.dylib"
    # elif platform.machine() == 'arm64':

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

SECRET_KEY 		= config('SECRET_KEY')
DEBUG 			= config('DEBUG', default=False, cast=bool)
# DEBUG = False
ALLOWED_HOSTS 	= config('ALLOWED_HOSTS', default='towerporchfest.org,www.towerporchfest.org').split(',')
# ALLOWED_HOSTS = ['localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
	'django_recaptcha',
    'phonenumber_field',
	'mapwidgets',
	'porches.apps.PorchesConfig',
    'performers',
	'website',
    'dashboard.apps.DashboardConfig',
    'planyourday',
    'anymail',
    'rest_framework',
    'rest_framework_gis',
]

LOGIN_URL                   = "dashboard:login"
LOGIN_REDIRECT_URL          = "dashboard:dashboard"
LOGOUT_REDIRECT_URL         = "dashboard:login"

RECAPTCHA_PUBLIC_KEY	    = config('RECAPTCHA_PUBLIC')
RECAPTCHA_PRIVATE_KEY	    = config('RECAPTCHA_PRIVATE')

MAPBOX_PUBLIC_KEY           = config('MAPBOX_PUBLIC_KEY')

PHONENUMBER_DEFAULT_REGION  = "US"

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
ANYMAIL                     = {"BREVO_API_KEY": config('BREVO_API_KEY'),}
DEFAULT_FROM_EMAIL          = "Porch Fest <info@towerporchfest.org>"
REST_FRAMEWORK              = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ]
}

MAP_WIDGETS = {
    "GoogleMap": {
        "apiKey": config('GOOGLE_MAP_API_KEY'),
        "CDNURLParams": {
            "language": "en",
            "libraries": "places,marker",
            "loading": "defer",
            "v": "quarterly",
        },
        "PointField": {
            "interactive": {
                "mapOptions": {
                    "zoom": 12,
                    "scrollwheel": False,
                    "streetViewControl": True,
                },
                "GooglePlaceAutocompleteOptions": {},
                "mapCenterLocationName": "Fresno, CA, USA",
                "markerFitZoom": 14,
            },
        },
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
		'ENGINE': 		'django.contrib.gis.db.backends.postgis',
		'NAME': 		config('POSTGRES_DB'),
		'USER': 		config('POSTGRES_USER'),
		'PASSWORD': 	config('POSTGRES_PASSWORD'),
		'HOST': 		config('POSTGRES_HOST', default='localhost'),
		'PORT': 		config('POSTGRES_PORT', default='5432'),
	}
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE   = 'en-us'
TIME_ZONE       = 'America/Los_Angeles'
USE_I18N        = True
USE_TZ          = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

BASE_URL            = config('BASE', default="https://towerporchfest.org")
STATIC_URL          = '/static/'
STATIC_ROOT         = BASE_DIR / 'staticfiles'
STATICFILES_DIRS    = [BASE_DIR / "static"]
MEDIA_URL           = '/media/'
MEDIA_ROOT          = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'