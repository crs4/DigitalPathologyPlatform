#  Copyright (c) 2019, CRS4
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, yaml, sys
from yaml.scanner import ScannerError
from yaml.error import YAMLError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_CONF_FILE_PATH = os.environ.get('DJANGO_CONFIG_FILE',
                                 os.path.join(BASE_DIR, 'config', 'config.yaml'))
cfg = None
try:
    with open(_CONF_FILE_PATH, 'r') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
except (IOError, ScannerError, YAMLError):
    pass
if cfg is None:
    sys.exit('Config file not found')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = cfg['django']['secret_key']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = cfg['django']['debug']

ALLOWED_HOSTS = cfg['django']['allowed_hosts']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'view_templates',
    'authentication',
    'slides_manager',
    'reviews_manager',
    'worklist_manager',
    'rois_manager',
    'clinical_annotations_manager',
    'odin',
    'utils',
    'questionnaires_manager',
    'shared_datasets_manager',
    'predictions_manager'
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'promort.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
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

WSGI_APPLICATION = 'promort.wsgi.application'

SESSION_EXPIRE_AT_BROWSER_CLOSE = cfg['django']['session_expire_on_close']

# Django logger
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s -- %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/promort.log',
            'maxBytes': 1024*1024*10,
            'backupCount': 10,
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARNING',
        },
        'promort': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'promort_commands': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}


# Database

if cfg['database']['engine'] == 'sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, cfg['database']['name']),
        }
    }
elif cfg['database']['engine'] == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': cfg['database']['name'],
            'USER': cfg['database']['user'],
            'PASSWORD': cfg['database']['password'],
            'HOST': cfg['database']['host'],
            'PORT': cfg['database']['port']
        }
    }
else:
    sys.exit('A valid database engine should be provided, exit')


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'GMT'

USE_I18N = True

USE_L10N = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

STATIC_ROOT = cfg['django']['static_root']

STATIC_SRC = './static_src/'

STATICFILES_DIRS = [
    (dirname, os.path.join(BASE_DIR, STATIC_SRC, dirname))
    for dirname in os.listdir(os.path.join(BASE_DIR, STATIC_SRC))
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    )
}

SESSION_COOKIE_NAME = cfg['django']['session_cookie']


# EMAIL SETTINGS
EMAIL_USE_TLS = cfg['email']['use_tls']
EMAIL_HOST = cfg['email']['host']
EMAIL_PORT = cfg['email']['port']
EMAIL_HOST_USER = cfg['email']['user']
EMAIL_HOST_PASSWORD = cfg['email']['password']
# REPORT SETTINGS
REPORT_SUBJECT_PREFIX = cfg['report']['subject_prefix']
REPORT_RECIPIENTS = cfg['report']['recipients']

# CUSTOM SETTINGS
SHARED_DATASETS_ENABLED = cfg['promort_config']['enable_shared_datasets']


DEFAULT_GROUPS = {
    'rois_manager': {
        'name': cfg['promort_groups']['rois_manager']['name'],
    },
    'clinical_manager': {
        'name': cfg['promort_groups']['clinical_manager']['name'],
    },
    'gold_standard': {
        'name': cfg['promort_groups']['gold_standard']['name'],
    },
    'odin_members': {
        'name': cfg['promort_groups']['odin_members']['name']
    },
    'prediction_manager': {
        'name': cfg['promort_groups']['prediction_manager']['name']
    }
}

OME_SEADRAGON_BASE_URL = cfg['ome_seadragon']['base_url']
OME_SEADRAGON_STATIC_FILES_URL = cfg['ome_seadragon']['static_files_url']

# app version
with open(os.path.join(BASE_DIR, 'VERSION')) as f:
    VERSION = f.readline()

ANNOTATION_SESSION_EXPIRED_TIME = cfg["annotation_session"]["expired_time"]
