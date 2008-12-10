import os, sys

sys.path.append('/var/www/praetorian/')
sys.path.append('/var/www/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'praetorian.settings_production'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
