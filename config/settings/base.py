"""
Django settings for config project.
Base settings to be imported by other settings files.
"""

import os
from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment configuration
ENVIRONMENT = config('ENVIRONMENT', default='development')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-=s24s@s)2l@1-bg4+5%x(l24&q0!h4eioqjx^c==-!nv!bi^h+')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Security: Only allow specific hosts in production  
allowed_hosts_str = config('ALLOWED_HOSTS', default='127.0.0.1,localhost')
if isinstance(allowed_hosts_str, str):
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]
else:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'apps.core',
    'apps.authentication',
    'apps.dashboard', 
    'apps.accounting',
    'apps.expenses',
    'apps.invoicing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.auth_redirect.AuthRedirectMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.analytics_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='westforce_removals'),
        'USER': config('DB_USER', default='westforce'),
        'PASSWORD': config('DB_PASSWORD', default='westforce123'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# User model
AUTH_USER_MODEL = 'authentication.User'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-au'

TIME_ZONE = 'Australia/Perth'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_collected')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
LOGIN_URL = 'authentication:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'landing_page'

COMPANY_NAME = config('COMPANY_NAME', default='Westforce Removals Company')
COMPANY_TAGLINE = config('COMPANY_TAGLINE', default='Professional Australian Removals Company Management System')

GOOGLE_ANALYTICS_ID = config('GOOGLE_ANALYTICS_ID', default='')
GOOGLE_TAG_MANAGER_ID = config('GOOGLE_TAG_MANAGER_ID', default='')
GOOGLE_ADS_ID = config('GOOGLE_ADS_ID', default='')
GOOGLE_ADS_CONVERSION_ID = config('GOOGLE_ADS_CONVERSION_ID', default='')
GOOGLE_ADS_PHONE_CONVERSION_LABEL = config('GOOGLE_ADS_PHONE_CONVERSION_LABEL', default='')
GOOGLE_ADS_EMAIL_CONVERSION_LABEL = config('GOOGLE_ADS_EMAIL_CONVERSION_LABEL', default='')
GOOGLE_ADS_QUOTE_CONVERSION_LABEL = config('GOOGLE_ADS_QUOTE_CONVERSION_LABEL', default='')

# Messages framework settings
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}
