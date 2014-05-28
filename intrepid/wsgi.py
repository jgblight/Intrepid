"""
WSGI config for intrepid project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "intrepid.settings")

from django.core.wsgi import get_wsgi_application
from django.conf import settings
from dj_static import Cling

class MediaCling(Cling):

    def __init__(self, application, base_dir=None):
        super(MediaCling, self).__init__(application, base_dir=base_dir)
        # override callable attribute with method
        self.debug_cling = self._debug_cling

    def _debug_cling(self, environ, start_response):
        environ = self._transpose_environ(environ)
        return self.cling(environ, start_response)

    def get_base_dir(self):
        return settings.MEDIA_ROOT

    def get_base_url(self):
        return settings.MEDIA_URL

application = Cling(MediaCling(get_wsgi_application()))
