"""
=============================================================================
DJANGO CONFIGURATION SETTINGS (settings.py)
=============================================================================
Beginner Explanation:
This file is the "Central Nervous System" or Master Control Center of your
entire Django web application. It defines:
1. Which apps are activated in this project (`INSTALLED_APPS`).
2. Where the database is stored and what engine to use (`DATABASES`).
3. How web requests flow through security and session filters (`MIDDLEWARE`).
4. Where templates (HTML files) and static files (CSS/JS/images) are located.
=============================================================================
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR represents the root folder where manage.py is located.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: Keep the secret key secret in production!
# In production, this should be read from an environment variable.
SECRET_KEY = 'django-insecure-smart-parking-management-super-secret-key-2026'

# SECURITY WARNING: Don't run with debug turned on in production!
# When DEBUG = True, Django shows detailed error stack traces if code crashes.
DEBUG = True

# Allowed hosts specifies which domain names or IP addresses can serve this app.
ALLOWED_HOSTS = ['*']

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================
# INSTALLED_APPS lists all packages and sub-applications active in your project.
# Django comes with built-in apps (admin, auth, sessions, messages), and we
# register our custom 'parking' app here so Django recognizes our models,
# migrations, and template files.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom Smart Parking Application
    'parking.apps.ParkingConfig',
]

# =============================================================================
# MIDDLEWARE
# =============================================================================
# Middleware is a framework of hooks into Django's request/response processing.
# Think of them as security guards standing at the door of your web application:
# they verify CSRF tokens, check user authentication, manage cookies and sessions.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Tells Django where the main URL routing pattern file lives.
ROOT_URLCONF = 'config.urls'

# =============================================================================
# TEMPLATES (HTML RENDERING ENGINE)
# =============================================================================
# Tells Django how to find, parse, and render HTML pages.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Global templates folder
        'APP_DIRS': True,                 # Also look inside parking/templates/
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# For development and college/demo projects, SQLite is built right into Python,
# requires zero external installation, and stores all tables in a single file: db.sqlite3.
# In enterprise production, you simply swap this with PostgreSQL or MySQL.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================
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

# =============================================================================
# INTERNATIONALIZATION & TIMEZONE
# =============================================================================
LANGUAGE_CODE = 'en-us'

# Set to local timezone or UTC
TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True

# =============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# =============================================================================
# STATIC_URL is the base URL prefix for serving static assets.
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type to use for models that do not define one.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
