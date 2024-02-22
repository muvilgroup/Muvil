from .settings import *

DATABASES = POSTGRE_MUVIL

ALLOWED_HOSTS = ["muvil.es", "www.muvil.es"]
CSRF_TRUSTED_ORIGINS = ['https://www.muvil.es', 'https://muvil.es']

DEBUG = False

USE_X_FORWARDED_HOST = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

MEDIA_URL = '/home/muvil_user/proyectos/Muvil/Muvil/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
