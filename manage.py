#!/usr/bin/env python
"""AnnaSutra Root CLI Wrapper.

Permits running Django management commands directly from the workspace root:
    python manage.py runserver
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py seed_demo_data
"""
import os
import sys
from pathlib import Path


def main():
    root_dir = Path(__file__).resolve().parent
    backend_dir = root_dir / "backend"

    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    os.chdir(str(backend_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH? Did you activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
