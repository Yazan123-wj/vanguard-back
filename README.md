# Vanguard Backend

Django REST API for the Vanguard site and admin panel.

## Deploy
Configured for Railway / Render (`Dockerfile`, `Procfile`, `render.yaml`).

Required env vars:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=0`
- `DJANGO_ALLOWED_HOSTS` (your host, e.g. `*.up.railway.app`)
- `CORS_ALLOWED_ORIGINS` (your Vercel front URL)
- `SITE_PUBLIC_URL` (your Vercel front URL)
- `ADMIN_API_TOKEN` (must match the front env)
- Optional: `DATABASE_URL` (Postgres). Without it, SQLite is used.

## Local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```
