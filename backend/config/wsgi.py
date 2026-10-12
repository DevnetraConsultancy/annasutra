"""WSGI config for AnnaSutra project."""
import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Ensure backend directory is in sys.path for serverless/container environments
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.dev"))
application = get_wsgi_application()
app = application
