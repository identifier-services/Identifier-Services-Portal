from ids.settings import *

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

MIDDLEWARE_CLASSES = [c for c in MIDDLEWARE_CLASSES if c !=
                      'ids_auth.middleware.AgaveTokenRefreshMiddleware']
