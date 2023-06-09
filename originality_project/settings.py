"""
Django settings for originality_project project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import logging
import os
from pathlib import Path

from django.conf import settings
from dotenv import load_dotenv, dotenv_values

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Build the path to the log file
log_file = os.path.join(BASE_DIR, 'logs', 'django.log')

# Configure logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',  # Set the desired log level
            'class': 'logging.FileHandler',
            'filename': log_file,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'DEBUG',  # Set the desired log level
            'propagate': True,
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
}

load_dotenv()  # take environment variables from .env.

config = dotenv_values(os.path.join(settings.BASE_DIR, ".env"))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'zudx3$9x^7*ib9wb&@ctul@dek&^avs-7(r4ref(+8kkxyrfvm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False,

ALLOWED_HOSTS = [
    '*',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'debug_toolbar',
    'django_bootstrap5',
    'settings_manager',
    'student',
    'teacher',
    'authentication',
    'services',
    'originality',
    'setup',
    'django.contrib.sites',  # must
    'allauth',  # must
    'allauth.account',  # must
    'allauth.socialaccount',  # must
    'allauth.socialaccount.providers.google',  # new

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',

]

ROOT_URLCONF = 'originality_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'libraries': {
                'custom_filters': 'originality_project.custom_filters',
            },
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

            ],
        },
    },
]

WSGI_APPLICATION = 'originality_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config.get("DATABASE_NAME"),
        'USER': config.get("DATABASE_USERNAME"),
        'PASSWORD': config.get("DATABASE_PASSWORD"),
        'PORT': config.get("DATABASE_PORT"),
        'HOST': config.get("DATABASE_HOST")
    }

}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UCT'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATICFILES_DIRS = [BASE_DIR / "assets"]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

INTERNAL_IPS = [
    '127.0.0.1',
]

# core/settings.py

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',

    # 'originality_project.provider.CustomGoogleProvider',

]
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {
            'prompt': 'select_account',
        }
    }
}

ACCOUNT_EMAIL_VERIFICATION = 'none'

LOGIN_REDIRECT_URL = '/'

# these are the required settings for Originality and Google Classroom
REQUIRED_ORIGINALITY_INTEGRATION_SETTINGS = [
    {
        "name": "key",
        "setting": ""
    },
    {
        "name": "originality_status",
        "setting": "True"
    },
    {
        "name": "ghost_writer_status",
        "setting": "True"
    },
    {
        "name": "api_url",
        "setting": ""
    },
    {
        "name": "google_client_id",
        "setting": ""
    },
    {
        "name": "google_client_secret",
        "setting": ""
    },
    {
        "name": "google_project_id",
        "setting": ""
    },
    {
        "name": "integration_version",
        "setting": "v0.1"
    }
]

REQUIRED_GROUPS = [
    "teachers", "students", "admins"
]
