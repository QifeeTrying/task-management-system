from pathlib import Path
from decouple import config
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')
INSTALLED_APPS = [
 'django.contrib.admin',
 'django.contrib.auth',
 'django.contrib.contenttypes',
 'django.contrib.sessions',
 'django.contrib.messages',
 'django.contrib.staticfiles',
 'django_celery_beat',
 'django_celery_results',

 # Third party
 'rest_framework',
 'rest_framework_simplejwt',
 'corsheaders',
 'django_filters',
 'drf_spectacular',

 # Local apps
 'apps.users',
 'apps.projects',
 'apps.tasks',
]
MIDDLEWARE = [
 'django.middleware.security.SecurityMiddleware',
 'corsheaders.middleware.CorsMiddleware',
 'django.contrib.sessions.middleware.SessionMiddleware',
 'django.middleware.common.CommonMiddleware',
 'django.middleware.csrf.CsrfViewMiddleware',
 'django.contrib.auth.middleware.AuthenticationMiddleware',
 'django.contrib.messages.middleware.MessageMiddleware',
 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [
 {
 'BACKEND': 'django.template.backends.django.DjangoTemplates',
 'DIRS': [],
 'APP_DIRS': True,
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
# Database
DATABASES = {
 'default': {
 'ENGINE': 'django.db.backends.postgresql',
 'NAME': config('DB_NAME', default='taskmanager'),
 'USER': config('DB_USER', default='postgres'),
 'PASSWORD': config('DB_PASSWORD', default='postgres'),
 'HOST': config('DB_HOST', default='localhost'),
 'PORT': config('DB_PORT', default='5432'),
 }
}
# Password validation
AUTH_PASSWORD_VALIDATORS = [
 {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
 {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
 {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
 {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
# Custom User Model
AUTH_USER_MODEL = 'users.User'
# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# REST Framework
REST_FRAMEWORK = {
 'DEFAULT_AUTHENTICATION_CLASSES': (
 'rest_framework_simplejwt.authentication.JWTAuthentication',
 ),
 'DEFAULT_PERMISSION_CLASSES': (
 'rest_framework.permissions.IsAuthenticated',
 ),
 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
 'PAGE_SIZE': 20,
 'DEFAULT_FILTER_BACKENDS': (
 'django_filters.rest_framework.DjangoFilterBackend',
 'rest_framework.filters.SearchFilter',
 'rest_framework.filters.OrderingFilter',
 ),
 'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
 'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
 'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
# CORS
CORS_ALLOWED_ORIGINS = [
 "http://localhost:3000",
 "http://127.0.0.1:3000",
]

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60 # 30 хвилин
# Celery Beat
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
# Email Configuration (для send_daily_report)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Для dev
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@taskmanager.com')