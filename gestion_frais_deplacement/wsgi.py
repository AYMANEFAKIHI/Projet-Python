import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_frais_deplacement.settings')
application = get_wsgi_application()
