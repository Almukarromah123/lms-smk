web: gunicorn lms_project.wsgi:application
release: python manage.py migrate && python manage.py collectstatic --noinput
