# Enhancement Alternates & Quick Fix Leads

Target: fast wins for attendance, leave, onboarding/requests, and document handling by leveraging open-source projects.

## Shortlist (ranked)
| Rank | Repo | Stars | Last Update | License | Why it helps | Risks/fit |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [Darsh-Jogi/Employee-Management-System](https://github.com/Darsh-Jogi/Employee-Management-System) | 37 | 2026-01-16 | (not listed) | MERN app with attendance + leave + salary views; React UI patterns reusable for our frontend | MERN stack; needs API swap to FastAPI and RBAC hardening |
| 2 | [notwld/AttendanceSystem](https://github.com/notwld/AttendanceSystem) | 14 | 2024-04-19 | (not listed) | FastAPI attendance API with Swagger; good starter for clock-in/out endpoints and models | Minimal tests; extend auth + persistence |
| 3 | [icecreamsandwich/react_lms](https://github.com/icecreamsandwich/react_lms) | 5 | 2022-09-21 | (not listed) | Simple React leave UI; can lift UI flows (apply, approve, history) for rapid theming | Old, no backend; needs styling + accessibility |
| 4 | [aneeshsunganahalli/HealthScan](https://github.com/aneeshsunganahalli/HealthScan) | 2 | 2025-11-30 | (not listed) | React + FastAPI document management with upload, OCR; good reference for file validation and previews | Health-specific; strip OCR, tighten HR RBAC |
| 5 | [OWASP/ASVS](https://github.com/OWASP/ASVS) | 9.3k | 2026-01-20 | CC BY-SA 3.0 | Security control catalog to benchmark auth/session/logging before adapting code | License is share-alike; use as checklist, not code |

## Recommendation
- **Adopt patterns, not full forks:** Use **AttendanceSystem** for backend models/routes for clock-in/out + leave accrual hooks, and **react_lms** for UI flow references. Style to our palette (Dark Blue/White/Pantone 284C/Green) and wire to existing FastAPI services.
- **Document upload guardrails:** Borrow validation and preview flow from **HealthScan** but keep uploads behind HR-only compliance routes; add size/type checks before enabling.
- **Security checklist:** Apply relevant ASVS controls (session, logging, file upload) when integrating the above.

## Adaptation Effort (high level)
- **Data model alignment:** Map attendance/leave schemas to our Employee Number anchor; add role checks (`admin`, `hr`, `viewer`, `manager`).
- **UI theming:** Reuse component structure; retheme with existing Tailwind palette and keyboard/focus states.
- **Testing:** Add API contract tests for attendance endpoints and snapshot tests for leave request UI once wired.
- **Deployment:** No infra changes expected; reuse current CI.

## Rollback
- Keep integrations behind feature flags; if issues arise, disable flags to revert to current flows without redeploying schema changes.
