from .base import *

AUTH_PASSWORD_VALIDATORS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': env('DATABASE_HOST'),
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
    }
}

RQ_QUEUES = {
    'default': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'ASYNC': False,
    },
    'high': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'ASYNC': False,
    },
    'low': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'ASYNC': False,
    },
    'scrapping': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'DEFAULT_TIMEOUT': 3600,
        'ASYNC': False,
    },
    'indexing': {
        'HOST': DEFAULT_REDIS_HOST,
        'PORT': DEFAULT_REDIS_PORT,
        'DB': DEFAULT_REDIS_DB,
        'ASYNC': False,
    },
}