import os
from pathlib import Path

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = '/app/staticfiles/'

# ... existing code ... 