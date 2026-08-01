# Vanguard Backend

Django REST API + Unfold admin for the Vanguard site.

## Stack
- Django 6 / DRF
- Postgres
- Pillow for uploads

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DJANGO_SECRET_KEY=your-secret
export POSTGRES_PASSWORD=your-password
python manage.py migrate
python manage.py runserver 8001
```

API defaults to `http://127.0.0.1:8001`.
