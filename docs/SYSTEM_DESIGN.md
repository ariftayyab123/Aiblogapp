# System Design: AI Blog Generator (Current State)

## 1) Product Goal
Build a user-owned AI blog platform where:
- users sign up and log in,
- authenticated users generate and manage their own blogs,
- each blog can be shared publicly via slug URL,
- public readers can submit `Helpful` / `Not helpful` feedback,
- owners see feedback analytics for only their own blogs.

## 2) Architecture Overview
- Frontend: React + Vite + Axios + Tailwind.
- Backend: Django + DRF + service-layer pattern.
- Async path: Celery + Redis (with sync fallback).
- DB: PostgreSQL.
- Auth: DRF token auth.

### Runtime modes
- Fast/MVP mode: synchronous generation (`QUEUE_ALWAYS_SYNC=True`).
- Scale mode: queued generation via Celery (`QUEUE_ALWAYS_SYNC=False`).

## 3) Local Runtime (Docker Compose)

Docker is used for local development parity and integration testing.

Container services:
- `frontend`: React/Vite UI
- `backend`: Django API
- `db`: PostgreSQL
- `redis`: queue/cache broker for async path
- `worker` (optional depending on compose profile): Celery worker

Local runtime flow:
1. Browser loads frontend container.
2. Frontend calls backend API container.
3. Backend writes/reads from PostgreSQL.
4. For async generation, backend publishes jobs to Redis and worker consumes them.

Environment usage:
- Local Docker can run either sync or async generation mode.
- For simplicity, local dev may keep sync fallback enabled while Redis/worker are optional.

## 4) Deployment Runtime Split

- Local/dev: Docker Compose for reproducible full-stack environment.
- Production/current plan: Vercel for both frontend and backend.
- Future scale option: introduce dedicated worker infrastructure only when traffic requires it.

## 5) Key Flows

### A. Auth flow
1. User registers via `POST /api/auth/register/` (`email`, `password`, `confirm_password`).
2. Backend returns token + user payload.
3. Frontend stores token in localStorage and sets authenticated state.
4. Protected routes unlock (`/`, `/blogs`, `/blog/:id`, `/analytics`).

### B. Blog generation flow
1. Authenticated user submits topic + persona.
2. `POST /api/generate/` starts sync generation or creates `GenerationJob`.
3. Frontend polls `GET /api/generation-status/:jobId/` when async.
4. On completion, blog is persisted with `owner=request.user`.

### C. Ownership and private data flow
- `GET /api/posts/`, `GET /api/posts/:id/`, and `DELETE /api/posts/:id/` are owner-scoped.
- Users cannot read/delete other users' private posts through internal APIs.

### D. Public sharing flow
1. Owner copies share URL: `/share/:slug`.
2. Public page calls `GET /api/posts/slug/:slug/public/`.
3. Public reader sees blog content and feedback controls only.
4. No navbar and no admin controls on shared page.

### E. Engagement + analytics flow
- Public reader submits `POST /api/engage/` with session ID.
- One reaction per session/blog pair enforced in backend.
- Owner opens `/analytics` and calls `GET /api/analytics/`.
- Analytics aggregates only owner's blogs.

## 6) Layered Design
- Views: thin orchestration and permission boundaries.
- Services: business logic (generation, engagement, auth service functions).
- Models: persistence and invariants (ownership, lifecycle state, uniqueness).
- Frontend API layer: request/response normalization and token injection.

## 7) Data Model Highlights
- `BlogPost.owner -> User` (ownership boundary).
- `GenerationJob.owner -> User` (keeps async ownership context).
- `Engagement` uses session + blog uniqueness for anonymous public reactions.

## 8) Security and Access Control
- Token auth required for private APIs.
- Public read path exists only for completed posts by slug.
- Shared page UI deliberately omits privileged actions.
- Auth token cleared automatically on 401 in frontend interceptor.

## 9) Scalability Path
Current:
- Vercel-friendly sync mode for speed.
- Optional queue fallback for local reliability.

Scale trigger path:
- Keep Vercel as primary for current plan.
- Introduce worker-based async infrastructure later only if traffic requires it.

## 10) Tradeoffs
- Session-based anonymous feedback lowers friction but has weaker identity guarantees.
- Token auth is sufficient for MVP but should evolve to refresh/JWT and stronger session controls in production.
- Sync generation is simpler but sensitive to timeout and long-response workloads.

## 11) Production Hardening Next Steps
1. Add stronger auth/session strategy (token rotation/expiry policy).
2. Add abuse controls for anonymous feedback (rate limits/device heuristics).
3. Increase automated frontend test depth for auth and shared-page edge cases.
4. Add observability alerts for generation failures/latency.

## 12) Route Map
Public routes:
- `/login`
- `/register`
- `/share/:slug`

Protected routes:
- `/` (generator)
- `/blogs`
- `/blog/:id`
- `/analytics`
