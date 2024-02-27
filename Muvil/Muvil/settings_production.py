from .settings import *

DATABASES = POSTGRE_MUVIL

ALLOWED_HOSTS = ["muvil.es", "www.muvil.es"]
CSRF_TRUSTED_ORIGINS = ['https://www.muvil.es', 'https://muvil.es']

DEBUG = True #se deja en True aunque sea produccion porque asi funcionan las media que suben los usuarios

USE_X_FORWARDED_HOST = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

PWA_APP_SCOPE = 'https://muvil.es/'
PWA_APP_START_URL = 'https://muvil.es/'
