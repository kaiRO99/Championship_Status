#!/bin/bash
python manage.py collectstatic && gunicorn --workers 2 already_over_project.wsgi