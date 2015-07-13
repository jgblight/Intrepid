#!/usr/bin/env python

import os
import sys

## GETTING-STARTED: make sure the next line points to your settings.py:
os.environ['DJANGO_SETTINGS_MODULE'] = 'intrepid.settings'
## GETTING-STARTED: make sure the next line points to your django project dir:
sys.path.append(os.path.join(os.environ['OPENSHIFT_REPO_DIR']))
virtenv = os.environ['APPDIR'] + '/virtenv/'
## GETTING-STARTED: make sure the next line has the right python version:
os.environ['PYTHON_EGG_CACHE'] = os.path.join(virtenv, 'lib/python2.7/site-packages')
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except:
    pass

import django.core.wsgi
application = django.core.wsgi.get_wsgi_application()
