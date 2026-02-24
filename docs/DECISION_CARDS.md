# Decision Cards (Current Architecture)

## D01
- Decision: Move from admin-first flow to open user signup/login.
- Need of use: Align with product expectation and reduce onboarding friction.
- Why this choice: Demonstrates full-stack user journey quickly.
- Alternative considered: Invite-code admin-only registration.
- Tradeoff accepted: Higher exposure to low-quality signups.
- Where it applies: Auth endpoints + frontend auth pages.
- Scaling path: Add email verification and abuse controls.
- Cross-exam hooks: Q01, Q02, Q18

## D02
- Decision: Enforce ownership on private blog APIs.
- Need of use: Protect user data isolation in multi-user environment.
- Why this choice: Clear security boundary with low complexity.
- Alternative considered: Single shared dataset with client-side filtering.
- Tradeoff accepted: Slightly stricter query logic.
- Where it applies: Blog viewset queryset + analytics filtering.
- Scaling path: Add org/team scopes if needed.
- Cross-exam hooks: Q03, Q06, Q19

## D03
- Decision: Keep public share page separate (`/share/:slug`).
- Need of use: Allow frictionless reading without auth.
- Why this choice: Supports viral sharing and realistic product behavior.
- Alternative considered: Auth-gated share links.
- Tradeoff accepted: Public exposure of completed shared content.
- Where it applies: Public slug endpoint + shared route/page.
- Scaling path: Add expiry/protection options per share link.
- Cross-exam hooks: Q04, Q11, Q20

## D04
- Decision: Keep anonymous feedback session-based.
- Need of use: Collect engagement before full reader accounts exist.
- Why this choice: Minimal friction for shared readers.
- Alternative considered: Login-only reactions.
- Tradeoff accepted: Weaker identity assurance.
- Where it applies: Engagement API + session context.
- Scaling path: Add optional authenticated feedback mode.
- Cross-exam hooks: Q11, Q12, Q19

## D05
- Decision: Keep Vercel sync mode + async queue path.
- Need of use: Ship fast while retaining scale migration lane.
- Why this choice: Fits interview time constraints and deployment simplicity.
- Alternative considered: Queue-only architecture from day one.
- Tradeoff accepted: Sync timeout risk under heavier loads.
- Where it applies: Generation view + settings queue flags.
- Scaling path: Move generation-primary traffic to async workers.
- Cross-exam hooks: Q05, Q06, Q07

## D06
- Decision: Use thin views and service-layer logic.
- Need of use: Maintain code clarity and testability.
- Why this choice: Faster safe iteration under time pressure.
- Alternative considered: Fat view/controller implementations.
- Tradeoff accepted: More files/classes to manage.
- Where it applies: Core/blog services + DRF views.
- Scaling path: Easier provider and feature expansion.
- Cross-exam hooks: Q01, Q02, Q08

## D07
- Decision: Keep centralized Axios interceptor for auth/error behavior.
- Need of use: Consistent transport policy across all frontend calls.
- Why this choice: Prevents per-call token and 401 logic duplication.
- Alternative considered: Manual header logic in every hook/page.
- Tradeoff accepted: Global interceptor must remain stable.
- Where it applies: `frontend/src/services/api.js`.
- Scaling path: Add telemetry and retry policy.
- Cross-exam hooks: Q14, Q16

## D08
- Decision: Use shared AuthLayout for login/register.
- Need of use: UI consistency and lower maintenance.
- Why this choice: Removes duplication and keeps branded auth UX aligned.
- Alternative considered: Separate page structures.
- Tradeoff accepted: Layout-level coupling between auth pages.
- Where it applies: `AuthLayout`, `LoginPage`, `RegisterPage`.
- Scaling path: Add auth-specific variants (forgot/reset/passwordless).
- Cross-exam hooks: Q10, Q18

## D09
- Decision: Keep analytics owner-scoped with refresh control.
- Need of use: Ensure analytics reflects latest personal blog performance.
- Why this choice: More trustworthy than stale or global data.
- Alternative considered: Global analytics feed.
- Tradeoff accepted: Less comparative benchmarking data.
- Where it applies: Analytics API + Analytics page refresh action.
- Scaling path: Add optional cohort/global benchmark mode.
- Cross-exam hooks: Q13, Q19

## D10
- Decision: Keep admin-register endpoint as non-primary.
- Need of use: Preserve operational flexibility without polluting user flow.
- Why this choice: Keeps backwards compatibility.
- Alternative considered: Remove endpoint immediately.
- Tradeoff accepted: Extra endpoint to maintain.
- Where it applies: Core auth views/serializers.
- Scaling path: Decommission when no longer needed.
- Cross-exam hooks: Q20
