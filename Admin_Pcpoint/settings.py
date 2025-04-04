
import pymysql
from pathlib import Path
import os

pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent # base path of root folder

SECRET_KEY = os.environ.get('SECRET_KEY','secretkey')
DEBUG = True # Set True for development, for production set it to False

ALLOWED_HOSTS = ['127.0.0.1', '.pythonanywhere.com', 'localhost']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'App_Pcpoint',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Admin_Pcpoint.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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


WSGI_APPLICATION = 'Admin_Pcpoint.wsgi.application'
PAYTM_MERCHANT_ID = 'ILVKZZ37013172738195'
PAYTM_SECRET_KEY = os.environ.get('PAYTM_SECRET_KEY')
PAYTM_WEBSITE = 'WEBSTAGING'
PAYTM_CHANNEL_ID = 'WEB'
PAYTM_INDUSTRY_TYPE_ID = 'Retail'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'chiragc612$pcpointdb',  # Correct database name
        'USER': 'chiragc612',  # Your PythonAnywhere username
        'PASSWORD': 'admin@123',  # Your MySQL password
        'HOST': 'chiragc612.mysql.pythonanywhere-services.com',  # PythonAnywhere MySQL host
        'PORT': '3306',
    }
}

# for locals MySql DB
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',  # Using MySQL
#         'NAME': 'pcpoint',  # Replace with your database name
#         'USER': 'root',  # Default MySQL user in XAMPP
#         'PASSWORD': '',  # XAMPP MySQL has no password by default (keep it empty)
#         'HOST': '127.0.0.1',  # Or 'localhost'
#         'PORT': '3306',  # Default MySQL port
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
#         }
#     }
# }


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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'  # Keeps static URL prefix
STATICFILES_DIRS = [  # Tells Django where to find static files for Development
    BASE_DIR / 'App_Pcpoint\static',  # This should contain your CSS, JS, images, etc.
]
STATIC_ROOT = BASE_DIR / 'static'  # Used for production when collecting static files

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
