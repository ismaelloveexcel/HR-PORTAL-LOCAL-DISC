# 🚨 URGENT CLEANUP PLAN

> **Created:** 2026-01-25  
> **Priority:** URGENT  
> **Status:** In Progress

---

## Execution Status

- [x] Phase 1: File cleanup (18 MD files, 12 images moved) ✅ COMPLETED
- [x] Phase 2: Workflow consolidation (4 redundant workflows removed) ✅ COMPLETED
- [ ] Phase 3: PR triage (recommendations provided - awaiting supervisor review)
- [x] Phase 4: Admin settings component created ✅ COMPLETED
  - ✅ Frontend component with UAE compliance fields
  - ✅ Backend API with settings persistence
  - ✅ Default workflows aligned with UAE labor law
- [ ] Phase 5: Aesthetic refresh (pending)

---

## Phase 1: Immediate Cleanup ✅ COMPLETED

### Root Directory - Obsolete Documentation (Move to archive or delete)
These files are either deprecated, PR-specific, or duplicates of docs/ content:

| File | Reason | Action |
|------|--------|--------|
| `DEPLOYMENT_FIX_INSTRUCTIONS.md` | One-time fix doc, outdated | DELETE |
| `DEPLOYMENT_FIX_SUMMARY.md` | One-time fix doc, outdated | DELETE |
| `DEPLOYMENT_REVISION_TRACKING.md` | One-time tracking doc | DELETE |
| `PR20_GUIDANCE.md` | PR-specific, merged | DELETE |
| `PR_18_REVIEW.md` | PR-specific, deprecated | DELETE |
| `MERGED_PR_REVISION_AUDIT.md` | Audit doc, no longer needed | DELETE |
| `DEPLOYMENT_CONTINUATION_ANALYSIS.md` | Analysis doc, superseded | DELETE |
| `DEPLOYMENT_STATUS_SUMMARY.md` | Superseded by START_HERE.md | DELETE |
| `WHAT_IS_HAPPENING.md` | Temporary doc | DELETE |
| `REVIEW_SUMMARY.md` | One-time review | DELETE |
| `DASHBOARD_QUICKSTART.md` | Duplicate of docs content | DELETE |
| `EXECUTIVE_SUMMARY.md` | Superseded | DELETE |
| `VISUAL_GUIDE.md` | Superseded | DELETE |
| `INDEX.md` | Duplicate entry point | DELETE |
| `index.md` | Duplicate entry point | DELETE |
| `preview-landing.md` | Preview doc | DELETE |
| `AZURE_DEPLOYMENT_REVIEW.md` | Review doc | DELETE |
| `DEPLOYED_APP_REVIEW.md` | Review doc | DELETE |

### Root Directory - Images (Move to docs/images/)
| File | Action |
|------|--------|
| `IMG_2072.jpg` | MOVE to docs/images/ |
| `IMG_2095.jpg` | MOVE to docs/images/ |
| `IMG_2096.png` | MOVE to docs/images/ |
| `IMG_2097.png` | MOVE to docs/images/ |
| `IMG_2098.jpg` | MOVE to docs/images/ |
| `IMG_2099.jpg` | MOVE to docs/images/ |
| `IMG_2100.png` | MOVE to docs/images/ |
| `image.jpg` | MOVE to docs/images/ |
| `image.png` | MOVE to docs/images/ |
| `image_01.png` | MOVE to docs/images/ |
| `image_02.png` | MOVE to docs/images/ |
| `image_05.png` | MOVE to docs/images/ |

---

## Phase 2: Workflow Consolidation

### Current Workflows (29 total) - REDUCE TO ~15

**KEEP (Essential):**
- `ci.yml` - Core CI
- `deploy.yml` - Main deployment
- `technical-guardian-health.yml` - Health monitoring
- `technical-guardian-security.yml` - Security scanning
- `aesthetic-guardian-pr.yml` - UI/UX review
- `azure-debugger-monitor.yml` - Failure analysis
- `code-quality-monitor.yml` - Quality checks
- `azure-deployment-engineer.yml` - Infra validation
- `pr-quality-check.yml` - PR validation
- `post-deployment-health.yml` - Post-deploy checks

**CONSOLIDATE/DELETE:**
- `backend.yml` → merge into `deploy.yml`
- `backend-appservice.yml` → merge into `deploy.yml`
- `backend-appservice-oidc.yml` → merge into `deploy.yml`
- `frontend-deploy.yml` → merge into `deploy.yml`
- `frontend-pr-check.yml` → merge into `pr-quality-check.yml`
- `deploy-local.yml` → DELETE (local dev only)
- `addon-discovery.yml` → REVIEW for necessity
- `github-pages.yml` → DELETE if not using GH Pages
- `audit-log.yml` → REVIEW
- `ssl-renewal-check.yml` → REVIEW
- `backup-db.yml` → REVIEW
- `daily-recruitment-automation.yml` → REVIEW
- `user-experience.yml` → REVIEW
- `security-monitoring.yml` → merge into security scan
- `automated-maintenance.yml` → REVIEW

---

## Phase 3: PR Triage

| PR # | Title | Recommendation |
|------|-------|----------------|
| #107 | Agent inventory (current) | MERGE after cleanup |
| #82 | Attendance pass | REVIEW - valuable feature |
| #76 | Remove Google Fonts | MERGE - good security |
| #71 | UX/Recruitment/Compliance | REVIEW - large PR |
| #69 | Recruitment docs | CLOSE - superseded |
| #68 | Onboarding blueprint | REVIEW |
| #59 | [WIP] Deploy HR portal | CLOSE - stale WIP |
| #55 | Remove hardcoded secrets | MERGE - security |
| #51 | Azure deployment workflow | CLOSE - superseded |
| #48 | Deploy automation trigger | CLOSE - superseded |
| #42 | SWA workflow fix | CLOSE - superseded |
| #41 | OIDC fallback | CLOSE - superseded |
| #38 | Split hosting arch | CLOSE - superseded |
| #37 | Frontend build fix | CLOSE - superseded |

---

## Phase 4: Admin Settings System

Create `/frontend/src/components/AdminSettings.tsx`:
- Toggle-based configuration
- Feature flags management
- Field visibility controls
- Workflow customization
- Non-technical friendly UI

---

## Phase 5: Aesthetic Refresh

### Design System
- **Primary:** White (#FFFFFF)
- **Text:** Dark Blue (#1E3A5F)
- **Accent:** Green (#10B981) - icons only
- **Warning:** Yellow (#F59E0B)
- **Error:** Red (#EF4444)
- **Neutral:** Gray (#6B7280)

### Icon Style
- Outline/stroke only
- 1.5px stroke weight
- Green color (#10B981)
- From Heroicons/Lucide

---

## Final Execution Status (Updated: 2026-01-25)

- [x] Phase 1: File cleanup ✅ COMPLETED
- [x] Phase 2: Workflow consolidation ✅ COMPLETED (27 workflows remaining, down from 31)
- [ ] Phase 3: PR triage ⚠️ REQUIRES SUPERVISOR DECISION
- [x] Phase 4: Admin settings ✅ COMPLETED & VERIFIED
- [ ] Phase 5: Aesthetic refresh 📋 READY TO START

---

## Phase 4 Verification Results ✅

### AdminSettings Component - UAE Compliance Verification

**Frontend Component:** `/frontend/src/components/AdminSettings/AdminSettings.tsx`
- ✅ Visa Number field (required, visible)
- ✅ Visa Expiry Date field (required, visible)
- ✅ Emirates ID field (required, visible)
- ✅ Emirates ID Expiry field (required, visible)
- ✅ Medical Fitness certificate tracking (optional, visible)
- ✅ ILOE Status tracking (optional, visible)

**Backend API:** `/backend/app/routers/admin.py` & `/backend/app/services/admin.py`
- ✅ GET /api/admin/settings - Load configurations
- ✅ PUT /api/admin/settings - Persist to database
- ✅ Settings stored in system_settings table
- ✅ JSON serialization for complex configurations

**Default Workflows - UAE Labor Law Alignment:**
1. ✅ Contract Renewal (Compliance category)
   - Tracks contract start/end dates
   - Reminder system for renewals
   - Aligned with UAE fixed-term contract requirements

2. ✅ Visa Renewal Alerts (Compliance category)
   - Visa expiry tracking
   - Automated notifications (60/30/7 day alerts recommended)
   - Prevents overstay violations

3. ✅ Medical Fitness Renewal (Compliance category)
   - Medical certificate expiry tracking
   - Renewal reminders
   - Required for visa renewals

4. ✅ Probation Review (HR category)
   - Probation end date tracking
   - Workflow for completion review
   - Aligned with UAE probation period rules (6 months max)

**UAE Compliance Coverage:**
| Requirement | Field/Workflow | Status |
|-------------|----------------|--------|
| Visa tracking | visa_number, visa_expiry + Visa Renewal workflow | ✅ Complete |
| Emirates ID | emirates_id, emirates_id_expiry | ✅ Complete |
| Medical fitness | medical_fitness + Medical Renewal workflow | ✅ Complete |
| Contract tracking | contract_type, contract_start/end + Contract Renewal | ✅ Complete |
| Probation period | probation_end + Probation Review workflow | ✅ Complete |
| ILOE/Insurance | iloe_status field | ✅ Complete |

**Missing (Future Enhancement):**
- ⚠️ Automated compliance alerts (60/30/7 day reminders)
- ⚠️ WPS salary payment tracking
- ⚠️ Working hours/overtime tracking (for timesheet module)
- ⚠️ Leave balance tracking per UAE labor law (30 days annual)

---
