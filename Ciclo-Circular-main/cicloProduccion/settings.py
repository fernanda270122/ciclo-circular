"""
Django settings for cicloProduccion project.
CONFIGURACIÓN HÍBRIDA: RENDER (NeonDB) + PYTHONANYWHERE (Postgres PA)
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
import mimetypes
import ssl
import certifi
ssl_context = ssl.create_default_context(cafile=certifi.where())

BASE_DIR = Path(__file__).resolve().parent.parent

# Carga variables de entorno locales si existen (.env)
load_dotenv(BASE_DIR / ".env")

# --- 1. SEGURIDAD BÁSICA ---
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-cambia-esto-en-produccion')

# Detección del entorno
EN_RENDER = 'RENDER' in os.environ
EN_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ

# Debug: True solo si NO estamos en producción o si se fuerza en .env
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Hosts permitidos
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
if EN_RENDER:
    ALLOWED_HOSTS.append('.onrender.com')
if EN_PYTHONANYWHERE:
    ALLOWED_HOSTS.append('.pythonanywhere.com')


# --- 2. BASE DE DATOS INTELIGENTE ---
DATABASES = {}

if EN_RENDER:
    # Render inyecta DATABASE_URL automáticamente
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600, 
        ssl_require=True
    )
    
elif EN_PYTHONANYWHERE:
    # PythonAnywhere: DATABASE_URL debe estar en tu archivo .env
    DATABASES['default'] = dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )

else:
    # --- MODO LOCAL (TU PC) ---
    DATABASES['default'] = dj_database_url.config(
        default='postgresql://ciclo_circular_db_user:Thj4j2hENjSvAD7QSY22igjyzSIwRmkv@dpg-d6o2fbk50q8c73dc9veg-a.oregon-postgres.render.com/ciclo_circular_db',
        conn_max_age=600
    )


# --- 3. APLICACIONES Y MIDDLEWARE ---
INSTALLED_APPS = [
    
    'admin_interface',
    'colorfield',
    'app',
    'user',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'rest_framework',
    'rest_framework.authtoken',
    'import_export', 
    'anymail', 
    
    'administrador',
    'api',  
    'django_extensions',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SITE_ID = 1 # Requerido por allauth

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Vital para Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",

]

ROOT_URLCONF = 'cicloProduccion.urls'

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

WSGI_APPLICATION = 'cicloProduccion.wsgi.application'

# --- 4. CONFIGURACIÓN DE USUARIO Y LOGIN ---
LOGIN_URL = '/user/account/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
AUTH_USER_MODEL = 'user.Usuario'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# --- 5. INTERNACIONALIZACIÓN ---
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC' 
USE_I18N = True
USE_TZ = True

# --- 6. ARCHIVOS ESTÁTICOS ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# --- 7. SEGURIDAD Y HTTPS ---
if EN_RENDER or EN_PYTHONANYWHERE:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

CSRF_TRUSTED_ORIGINS = [
    'https://*.pythonanywhere.com',
    'https://*.onrender.com'
]

# --- 8. CORREO Y API KEYS ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
    ],
}

IMPORT_EXPORT_USE_TRANSACTIONS = True     

# Variables Externas
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- CONFIGURACIÓN DE EMAIL (BREVO API) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 30
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_HOST_USER = 'a4ba9b001@smtp-brevo.com'
EMAIL_HOST_PASSWORD = 'UPLM92nEtK50FTcD'
DEFAULT_FROM_EMAIL = 'corp.ici.uchile@gmail.com'



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

mimetypes.add_type("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx", True)




# ==========================================
# CONFIGURACIÓN MERCADO PAGO
# ==========================================
MERCADOPAGO_ACCESS_TOKEN = os.getenv('MERCADOPAGO_ACCESS_TOKEN')




# ==========================================
# CONFIGURACIÓN DE LOGIN CON GOOGLE
# ==========================================
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none' # Para que no les pida confirmar el correo, ya que Google ya lo verificó

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': '803400138801-eq8ps1jt43lg4puqpn88p12qm92pmvq5.apps.googleusercontent.com',
            'secret': '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',
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
# Para que si un alumno ya existía con ese correo, Google se vincule automáticamente a su cuenta

SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_LOGIN_ON_GET = True


GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')