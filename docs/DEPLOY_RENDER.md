# Deploy Backend on Render (Django + PostgreSQL + Redis + Celery)

This guide deploys the `backend/` service first so the Vercel frontend can call a live API.

## 1. Push Latest Code
From repo root:

```bash
git add backend/ai_blog/settings.py backend/requirements.txt backend/.env.example docker-compose.yml render.yaml docs/DEPLOY_RENDER.md
git commit -m "Prepare backend for Render deployment"
git push origin main
```

## 2. Create Services on Render
1. In Render, click **New +** -> **Blueprint**.
2. Connect your GitHub repo.
3. Select this repo and deploy using `render.yaml`.

This blueprint creates:
- `ai-blog-backend` (web service)
- `ai-blog-worker` (Celery worker)
- `ai-blog-redis`
- `ai-blog-db`

## 3. Set Required Secrets in Render
After blueprint creation, open both `ai-blog-backend` and `ai-blog-worker` and set:
- `ANTHROPIC_API_KEY` (or use Gemini vars if `LLM_PROVIDER=gemini`)
- `CORS_ALLOWED_ORIGINS=https://<your-vercel-domain>`
- `CSRF_TRUSTED_ORIGINS=https://<your-backend>.onrender.com,https://<your-vercel-domain>`

Optional for Vercel preview domains:
- `CORS_ALLOWED_ORIGIN_REGEXES=https://.*\\.vercel\\.app`

## 4. Deploy and Verify Backend
1. Trigger deploy for `ai-blog-backend` and `ai-blog-worker`.
2. Check health:
   - `https://<your-backend>.onrender.com/health/live` should return `200`.
   - `https://<your-backend>.onrender.com/health/ready` should return `200` when DB + Redis are connected.
3. Check API:
   - `https://<your-backend>.onrender.com/api/personas/`

## 5. Use Backend URL in Vercel
In Vercel frontend project env vars:

```text
VITE_API_URL=https://<your-backend>.onrender.com/api
```

## 6. Common Issues
- `ImproperlyConfigured ANTHROPIC_API_KEY`: set real provider key on both web and worker.
- `QUEUE_UNAVAILABLE`: worker or Redis is not running.
- `CORS blocked`: backend `CORS_ALLOWED_ORIGINS` missing your Vercel domain.
