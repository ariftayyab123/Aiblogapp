# AI Blog Generator

AI-assisted blog generation platform built with Django (DRF) and React.

Current product flow:
- users sign up and log in,
- authenticated users generate and manage their own blogs,
- blogs can be shared publicly with a URL,
- public readers can submit `Helpful` / `Not helpful` feedback,
- owners see analytics for their own posts.

## Features

- AI blog generation with persona-based writing styles
- Owner-scoped blogs (private management per user)
- Public shared blog pages via slug URL
- Anonymous helpfulness feedback on shared pages
- Owner-only analytics dashboard
- Auth pages with shared branded layout (`AuthLayout`)
- Service-layer backend architecture (thin views, business services)

## Tech Stack

### Backend
- Django + Django REST Framework
- PostgreSQL
- Celery + Redis (async generation path)
- Anthropic and/or Gemini provider integration

### Frontend
- React + Vite
- Tailwind CSS
- React Router
- Axios (centralized API interceptor)

## Application Routes

### Public routes
- `/login`
- `/register`
- `/share/:slug`

### Protected routes (auth required)
- `/` (blog generator)
- `/blogs`
- `/blog/:id`
- `/analytics`

## API Endpoints (Current)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | User signup (`email`, `password`, `confirm_password`) |
| POST | `/api/auth/token/` | User login (returns token + user) |
| GET | `/api/personas/` | List active personas |
| POST | `/api/generate/` | Generate blog (auth required) |
| GET | `/api/generation-status/{job_id}/` | Poll async generation status (auth required) |
| GET | `/api/posts/` | List current user's posts |
| GET | `/api/posts/{id}/` | Get current user's post by id |
| DELETE | `/api/posts/{id}/` | Delete current user's post |
| GET | `/api/posts/slug/{slug}/public/` | Public shared post view |
| POST | `/api/engage/` | Submit helpful/not-helpful feedback |
| GET | `/api/posts/{id}/engagement/` | Get feedback metrics for a post |
| GET | `/api/analytics/` | Owner-scoped analytics |

## Quick Start

## 1) Local (without Docker)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loadpersonas
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Backend: `http://localhost:8000`  
Frontend: `http://localhost:5173`

## 2) Docker Compose

```bash
# From repo root
cp .env.example .env
# Fill required keys in .env

docker-compose up --build

# First-time setup
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py loadpersonas
```

## Environment Variables

Core:
- `DJANGO_SECRET_KEY`
- `DATABASE_URL`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`

Model providers:
- `ANTHROPIC_API_KEY` and/or `GEMINI_API_KEY`

Generation mode:
- `QUEUE_ALWAYS_SYNC` (`True` for Vercel-friendly MVP mode)
- `QUEUE_SYNC_FALLBACK` (`True` to fallback when queue is unavailable)
- `REDIS_URL` (required for async queue mode)

Frontend:
- `VITE_API_URL` (example: `http://localhost:8000/api`)
- `VITE_API_TOKEN` (optional dev fallback only)

## Architecture Summary

Service-oriented layered architecture:

1. Presentation: React pages/components/hooks/contexts
2. API layer: DRF views + serializers
3. Service layer: business logic (generation, engagement, auth services)
4. Data layer: Django models + PostgreSQL
5. External layer: AI providers and queue infrastructure

Key boundary decisions:
- Private data is enforced server-side with owner filtering.
- Public sharing is isolated to slug endpoint and share page.
- Anonymous feedback uses session dedupe for low-friction engagement.

## Project Structure

```txt
backend/
  ai_blog/
    settings.py
    urls.py
    apps/
      blog/
      core/
frontend/
  src/
    components/
    contexts/
    hooks/
    pages/
    services/
docs/
docker-compose.yml
README.md
```

## Testing and Quality

### Backend tests
```bash
cd backend
python manage.py test
```

### Frontend build check
```bash
cd frontend
npm run build
```

## Documentation

See `docs/` for system design materials:
- `docs/SYSTEM_DESIGN.md`

## License

MIT
