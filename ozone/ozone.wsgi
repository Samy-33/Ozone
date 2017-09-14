import os
import sys
import site

site.addsitedir('/home/saras/Documents/Ozone/env/lib/python3.6/site-packages')

sys.path.append('/home/saras/Documents/Ozone')
sys.path.append('/home/saras/Documents/Ozone/ozone')

os.environ['DJANGO_SETTINGS_MODULE'] = 'ozone.settings'

activate_env=os.path.join(os.getcwd(), 'env/bin/activate_this.py')
execfile(activate_env, dict(__file__=activate_env))

import django.core.handlers.wsgi
application = django.core.hadlers.wsgi.WSGIHandler()
