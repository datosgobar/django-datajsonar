#! coding: utf-8
import os
import environ
from os.path import dirname

from django_datajsonar import strings

SETTINGS_DIR = environ.Path(__file__) - 1
ROOT_DIR = environ.Path(__file__) - 3  # (/a/b/myfile.py - 3 = /)
APPS_DIR = ROOT_DIR.path(dirname(dirname(dirname(__file__))))

env = environ.Env()
environ.Env.read_env(SETTINGS_DIR('.env'))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_ROOT = str(APPS_DIR('media'))
MEDIA_URL = '/media/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5)h719h9vs0f^i8h9ptt_7g%-&u^4e!yy475-b96g#t3nrqmh1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition


DJANGO_BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

VENDOR_APPS = [
    'scheduler',
    'django_rq',
    'solo',
]

APPS = [
    'django_datajsonar',
]

INSTALLED_APPS = DJANGO_BASE_APPS + VENDOR_APPS + APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

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

WSGI_APPLICATION = 'conf.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "formatters": {
        "rq_console": {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%H:%M:%S",
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        "rq_console": {
            "level": "DEBUG",
            "class": "rq.utils.ColorizingStreamHandler",
            "formatter": "rq_console",
            "exclude": ["%(asctime)s"],
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
        },
        'apps': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'filters': ['require_debug_true'],
            "formatter": "simple",
        },
        'production': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'filters': ['require_debug_false'],
            "formatter": "verbose",
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'series_tiempo_ar_api': {
            'handlers': ['apps', 'production'],
            'level': 'INFO',
            'propagate': False,
        },
        "rq.worker": {
            "handlers": ["rq_console", ],
            "level": "DEBUG"
        },
    }
}


DEFAULT_REDIS_HOST = env("DEFAULT_REDIS_HOST", default="localhost")
DEFAULT_REDIS_PORT = env("DEFAULT_REDIS_PORT", default="6379")
DEFAULT_REDIS_DB = env("DEFAULT_REDIS_DB", default="0")

RQ_QUEUES = {
    'default': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
    },
    'high': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
    },
    'low': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
    },
    'scrapping': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'DEFAULT_TIMEOUT': 3600,
    },
    'indexing': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
    },
}

DISTRIBUTION_INDEX_JOB_TIMEOUT = 100

CATALOG_BLACKLIST = [
    "themeTaxonomy"
]

DATASET_BLACKLIST = [

]

DISTRIBUTION_BLACKLIST = [
    "scrapingFileSheet"
]

FIELD_BLACKLIST = [
    "scrapingDataStartCell",
    "scrapingIdentifierCell",
    "scrapingDataStartCell",
]

DEFAULT_TASKS = [
    {
        'name': 'Read Datajson Task',
        'callable': 'django_datajsonar.tasks.schedule_new_read_datajson_task',
        'start_hour': 3,
        'start_minute': 0,
        'interval': 6,
        'interval_unit': 'hours'
    },
    {
        'name': 'Close Indexing Task',
        'callable': 'django_datajsonar.indexing.tasks.close_read_datajson_task',
        'start_hour': 3,
        'start_minute': 15,
        'interval': 30,
        'interval_unit': 'minutes'
    }
]

DEFAULT_PROCESSES = [
    {
        'name': "Indexing x 2",
        'stages': [
            {
                'callable_str': 'django_datajsonar.tasks.schedule_new_read_datajson_task',
                'queue': 'indexing',
                'task': 'django_datajsonar.models.ReadDataJsonTask'

            },
            {

                'callable_str': 'django_datajsonar.tasks.schedule_new_read_datajson_task',
                'queue': 'indexing'
            },
            {
                'callable_str': 'django_datajsonar.indexing.tasks.close_read_datajson_task',
                'queue': 'default'
            }
        ],
    }
]

STAGES_TITLES = {
    'METADATA_READ': 'Read Datajson (metadata only)',
    'COMPLETE_READ': 'Read Datajson (complete)',
}

DATAJSONAR_STAGES = {
    STAGES_TITLES['COMPLETE_READ']: {
        'callable_str': 'django_datajsonar.tasks.schedule_full_read_task',
        'queue': 'indexing',
        'task': 'django_datajsonar.models.ReadDataJsonTask',
    },
    STAGES_TITLES['METADATA_READ']: {
        'callable_str': 'django_datajsonar.tasks.schedule_metadata_read_task',
        'queue': 'indexing',
        'task': 'django_datajsonar.models.ReadDataJsonTask',
    },
}

SYNCHRO_DEFAULT_CONF = [
    {
        'title': 'Lectura de metadata de red',
        'stages': [STAGES_TITLES['METADATA_READ']],
        'scheduled_time': '04:00',
    },
    {
        'title': 'Lectura completa de red',
        'stages': [STAGES_TITLES['COMPLETE_READ']],
        'scheduled_time': '15:00',
        'week_days': strings.WEEK_DAYS
    },
]
