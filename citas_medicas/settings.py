"""
Django settings for citas_medicas project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno
load_dotenv(os.path.join(BASE_DIR, '.env'))

# ==================== SEGURIDAD ====================
SECRET_KEY = 'django-insecure-en9k*-5*nr4+)ejg+byld%3z42md=axgl!27^m3csm9z-aqb_t'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# ==================== APLICACIONES ====================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    'pacientes',
    'medicos',
    'citas',
    'autenticacion',
]

# ==================== MIDDLEWARE ====================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'autenticacion.middleware.LoginRequiredMiddleware',
    'autenticacion.middleware.RolMiddleware',
]

ROOT_URLCONF = 'citas_medicas.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'citas_medicas.wsgi.application'

# ==================== BASE DE DATOS ====================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'citas_medicas_db'),
        'USER': os.getenv('DB_USER', 'citas_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', '12345'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ==================== VALIDACIÓN DE CONTRASEÑAS ====================
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

# ==================== INTERNACIONALIZACIÓN ====================
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Managua'
USE_I18N = True
USE_TZ = True

# ==================== ARCHIVOS ESTÁTICOS ====================
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== CORS ====================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003",
    "http://localhost:8004",
    "http://localhost:8005",
]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ==================== REST FRAMEWORK ====================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# ==================== SIMPLE JWT ====================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# ==================== AUTENTICACIÓN DJANGO ====================
# ¡¡¡IMPORTANTE: CAMBIA SOLO ESTA LÍNEA!!!
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/app/'  # ¡¡¡CAMBIA DE '/' A '/app/'!!!
LOGOUT_REDIRECT_URL = '/login/'

# ==================== LOGGING ====================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# ==================== URLs DE APIs EXTERNAS ====================
AUTH_API_URL = os.getenv('AUTH_URL', 'http://localhost:8005')
ESPECIALIDADES_API_URL = os.getenv('ESPECIALIDADES_URL', 'http://localhost:8001')
MEDICOS_API_URL = os.getenv('MEDICOS_URL', 'http://localhost:8002')
PACIENTES_API_URL = os.getenv('PACIENTES_URL', 'http://localhost:8003')
CITAS_API_URL = os.getenv('CITAS_URL', 'http://localhost:8004')
GATEWAY_API_URL = os.getenv('GATEWAY_URL', 'http://localhost:8000')