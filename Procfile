web: gunicorn vanguard_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60
release: python manage.py migrate --noinput
