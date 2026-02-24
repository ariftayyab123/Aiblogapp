# Fullstack Deploy on Vercel (Frontend + Backend)

This repo is deployed as **two Vercel projects**:
1. Frontend project (`rootDir=frontend`)
2. Backend project (`rootDir=backend`)

## 1) Deploy Backend on Vercel

### Project settings
- Framework preset: `Other`
- Root Directory: `backend`
- Install Command: `pip install -r requirements.txt`
- Build Command: leave empty (or default)
- Output Directory: leave empty

Backend runtime routing already exists:
- `backend/vercel.json` routes all requests to `api/wsgi.py`

### Required backend env vars
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `ALLOWED_HOSTS=<your-backend-domain>.vercel.app`
- `CORS_ALLOWED_ORIGINS=https://<your-frontend-domain>.vercel.app`
- `CSRF_TRUSTED_ORIGINS=https://<your-frontend-domain>.vercel.app`
- `DATABASE_URL=<managed-postgres-url>`
- `LLM_PROVIDER=anthropic` (or `gemini`)
- `ANTHROPIC_API_KEY` and model vars (if anthropic)
- `GEMINI_API_KEY` and model vars (if gemini)
- `QUEUE_ALWAYS_SYNC=True` (recommended on Vercel serverless)
- `QUEUE_SYNC_FALLBACK=True`

Optional:
- `REDIS_URL` (only if you later run async queue infra)

### One-time backend bootstrap
Run once against production DB:
```bash
cd backend
python manage.py migrate
python manage.py loadpersonas
```

## 2) Deploy Frontend on Vercel

### Project settings
- Framework preset: `Vite`
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`

Frontend routing rewrite already exists:
- `frontend/vercel.json`

### Required frontend env vars
- `VITE_API_URL=https://<your-backend-domain>.vercel.app/api`

Optional:
- `VITE_API_TOKEN` (dev-only fallback; not required for normal user auth flow)

## 3) Verify Production Flow
1. Open frontend URL.
2. Register user at `/register`.
3. Login and generate blog.
4. Open shared URL `/share/:slug` in another browser.
5. Submit helpful/not-helpful feedback.
6. Check owner analytics in `/analytics`.

## Notes
- This project currently uses token auth and owner-scoped APIs.
- Shared page is public by design and has no navbar/admin controls.
- For heavy generation load, migrate generation traffic to worker-based async infrastructure later.
