# Deploy on Vercel (Frontend) + Hosted Django API

This app has two runtimes:
- Frontend (React/Vite): deploy to Vercel.
- Backend (Django + PostgreSQL + Redis/Celery): deploy to a backend platform (Render/Railway/Fly/etc).

Vercel does not run long-lived Celery workers, so background generation workers should stay on backend infrastructure.

## 1. Deploy Backend First
Deploy `backend/` to your backend host and set environment variables:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `ALLOWED_HOSTS=<your-backend-host>`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `LLM_PROVIDER`
- Provider keys/models:
  - Anthropic: `ANTHROPIC_API_KEY`, `CLAUDE_MODEL`, `CLAUDE_FAST_MODEL`
  - Gemini: `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_FAST_MODEL`
- Queue/cache:
  - `REDIS_URL`
  - `QUEUE_SYNC_FALLBACK` (optional)

Then run migrations and (if needed) `loadpersonas`.

## 2. Configure Backend CORS for Vercel
Set on backend:
- `CORS_ALLOWED_ORIGINS=https://<your-vercel-domain>`
- Optional preview support:
  - `CORS_ALLOWED_ORIGIN_REGEXES=https://.*\\.vercel\\.app`

## 3. Deploy Frontend to Vercel
In Vercel:
1. Import repo.
2. Set **Root Directory** to `frontend`.
3. Build settings:
   - Install command: `npm install`
   - Build command: `npm run build`
   - Output directory: `dist`
4. Add environment variables:
   - `VITE_API_URL=https://<your-backend-domain>/api`
   - `VITE_BLOG_ID_SECRET=<strong-random-secret>`
   - `VITE_API_TOKEN=<optional-admin-token-if-needed>`
5. Deploy.

`frontend/vercel.json` is included to rewrite SPA routes to `index.html`.

## 4. Post-Deploy Verification
1. Open frontend URL and load home page.
2. Check `/blogs` and `/analytics`.
3. Generate a post:
   - If async is enabled, ensure backend Redis + Celery worker are running.
4. Confirm browser network calls go to `https://<backend>/api/...` and CORS is successful.

## 5. Common Issues
- `CORS blocked`: backend `CORS_ALLOWED_ORIGINS` missing Vercel domain.
- `Generation slow`: Redis/Celery worker not running, fallback sync path in use.
- `401/403`: set `ADMIN_AUTH_REQUIRED` appropriately and provide token when required.
