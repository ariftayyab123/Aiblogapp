# Admin/Auth and Public Sharing (Current Behavior)

This project follows a user-centric auth model.

## Current auth model
- Primary flow: open user signup + login.
- Endpoint: `POST /api/auth/register/`.
- Endpoint: `POST /api/auth/token/`.
- Token is stored client-side and attached to API requests.

## Legacy admin endpoint
- `POST /api/auth/admin/register/` still exists in backend for optional operations.
- It is not part of the primary user journey.

## Sharing model
- Internal owner view: `/blog/:id` (owner-scoped).
- Public shared view: `/share/:slug`.
- Public data source: `GET /api/posts/slug/<slug>/public/`.

## What shared readers can do
- Read completed post content.
- Submit `Helpful` / `Not helpful` feedback.

## What shared readers cannot do
- Access owner dashboard routes.
- Delete posts.
- Use private analytics endpoints.

## Ownership boundaries
- Private post APIs are filtered by `owner=request.user`.
- Analytics is computed only across the authenticated owner's posts.

## UX contract
- Navbar hidden on `/share/:slug`.
- Navbar hidden on auth pages (`/login`, `/register`) for focused onboarding.
- Auth pages use a shared branded layout component for consistency.
