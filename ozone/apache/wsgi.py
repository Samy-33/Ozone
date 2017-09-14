#wsgi.py
import os, sys
# Calculate the path based on the location of the WSGI script.
apache_configuration= os.path.dirname(__file__)
project = os.path.dirname(apache_configuration)
workspace = os.path.dirname(project)
sys.path.append(workspace)
sys.path.append(project)

# # Add the path to 3rd party django application and to django itself.
# sys.path.append('/var/wwww/Ozone/')
# sys.path.append('var/www/Ozone/env/lib/python3.6/site-packages/')
# os.environ['DJANGO_SETTINGS_MODULE'] = 'ozone.settings'

# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()

# import os

import logging
logging.basicConfig(stream=sys.stderr)


from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ozone.settings")

application = get_wsgi_application()
