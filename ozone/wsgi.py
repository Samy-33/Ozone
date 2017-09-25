# wsgi.py
import logging
import os
import sys

from django.core.wsgi import get_wsgi_application

# Calculate the path based on the location of the WSGI script.

apache_configuration = os.path.dirname(__file__)
project = os.path.dirname(apache_configuration)
workspace = os.path.dirname(project)
sys.path.append(workspace)
sys.path.append(project)

logging.basicConfig(stream=sys.stderr)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ozone.settings")

application = get_wsgi_application()
