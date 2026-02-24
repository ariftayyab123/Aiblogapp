"""
WSGI entrypoint for Vercel Python runtime.
Routes all requests to the Django application.
"""
import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_blog.settings')

app = get_wsgi_application()
