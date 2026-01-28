# PASS SYSTEM ARCHITECTURE — Comprehensive Review & Proposal

**Document Status:** Technical Proposal  
**Date:** January 2025  
**Agent:** Guardian HR-UAE  
**Purpose:** Evaluate current Pass implementations, identify gaps, and propose solutions for interlinking, employee access, and labor law integration

---

## EXECUTIVE SUMMARY

The Pass system is HR Harem's **core innovation** for keeping users informed without phone/email follow-ups. This review analyzes:

1. **Current State:** What's working, what's incomplete
2. **Gaps Identified:** Missing features against stated requirements
3. **Technical Proposals:** Architecture solutions for interlinking, employee access, and labor law quotes
4. **Implementation Roadmap:** Phased rollout with UAE compliance-first approach

**Key Finding:** The foundation is **solid and well-architected**, but 3 critical features are missing:
- Onboarding Pass frontend UI (backend exists)
- Employee Request Passes (probation, visa renewal, etc.)
- Labor law quote validation system

---

## 1. CURRENT STATE ANALYSIS

### 1.1 What EXISTS and is WORKING ✅

#### **A. Manager Pass** (`frontend/src/components/ManagerPass/ManagerPass.tsx`)
- **Status:** ✅ Fully implemented (1160 lines)
- **Features:**
  - Journey timeline with 5 stages (Request → Screening → Interview → Decision → Onboarding)
  - Action Required section (dynamic based on status)
  - Activity history
  - Document management (JD, Recruitment Form)
  - Interview slot provision via `InterviewSlotProvider`
  - Candidate pipeline stats
  - Pass metrics dashboard
  - QR code sharing
  - WhatsApp/Email contact
- **Entity Support:** ✅ Multi-company recruitment (Agriculture, IT, etc.)
- **Assessment:** **Production-ready**. Well-structured, follows design system.

#### **B. Candidate Pass** (`frontend/src/components/CandidatePass/CandidatePass.tsx`)
- **Status:** ✅ Fully implemented (995 lines)
- **Features:**
  - Journey timeline (5 stages, candidate-facing labels)
  - Action Required section
  - Activity history
  - Document upload
  - Interview slot selection via `InterviewSlotSelector`
  - Candidate details confirmation form
  - QR code sharing
  - WhatsApp/Email contact
- **Assessment:** **Production-ready**. Clean UX, mobile-optimized.

#### **C. BasePass Component System** (`frontend/src/components/BasePass/`)
- **Status:** ✅ Mature architecture
- **Components:**
  - `BasePassContainer.tsx` — Unified card structure with tabs
  - `PassHeader.tsx` — Consistent header design
  - `ActionRequired.tsx` — Next action display
  - `JourneyTimeline.tsx` — Visual progress tracker
  - `ActivityHistory.tsx` — Event log
  - `StatusBadge.tsx` — Status indicators
  - `entityTheme.ts` — Multi-company theming
  - `actionUtils.ts` — Workflow logic (LOCKED GOVERNANCE)
- **Assessment:** **Excellent foundation**. Reusable, consistent, well-documented.

#### **D. Pass Interlinking (Manager ↔ Candidate)**
- **Status:** ✅ **WORKING** via `InterviewSlot` models
- **Mechanism:**
  1. Manager provides slots → `InterviewSlotProvider.tsx`
  2. Slots saved to `interview_slots` table
  3. Candidate sees slots → `InterviewSlotSelector.tsx`
  4. Candidate books slot → Status updates to "scheduled"
  5. Both passes reflect booking in real-time
- **Database Schema:** `backend/app/models/interview.py`
  - `InterviewSetup` → Configuration
  - `InterviewSlot` → Available times
  - `booked_by_candidate_id` → Links candidate
  - `candidate_confirmed` → Confirmation flag
- **Assessment:** **This is exactly what was requested**. Interlinking works bidirectionally.

#### **E. Nomination Pass** (`frontend/src/components/NominationPass/NominationPass.tsx`)
- **Status:** ✅ Implemented for EOY nominations
- **Features:**
  - Manager verification flow
  - Employee selection
  - Nomination form with categories
  - Countdown to deadline
  - Success confirmation
- **Assessment:** Different use case (annual process) but demonstrates Pass pattern versatility.

#### **F. Backend Pass Infrastructure**
- **Models:** `backend/app/models/passes.py` — Generic Pass model
- **Schemas:** `backend/app/schemas/interview.py` — `CandidatePassData`, `ManagerPassData`
- **Routes:** `backend/app/routers/interview.py` — Pass data endpoints
- **Services:** `backend/app/services/interview_service.py` — Pass data assembly
- **Assessment:** **Well-structured**. API-first design, clear separation of concerns.

---

### 1.2 What is PARTIALLY IMPLEMENTED ⚠️

#### **Onboarding Pass**
- **Backend:** ✅ **Exists** (`backend/app/routers/onboarding.py`, `backend/app/services/onboarding.py`)
  - Token generation: `/onboarding/invite`
  - Token validation: `/onboarding/validate/{token}`
  - Welcome info: `/onboarding/welcome/{token}`
  - Profile submission: `/onboarding/submit/{token}`
- **Frontend:** ⚠️ **Basic HTML form only** (in `App.tsx` lines 1218-1350)
  - Shows onboarding form
  - **NOT styled as a Pass** (no BasePass components)
  - **No journey timeline** (5 onboarding stages defined in `actionUtils.ts` but unused)
  - **No action tracking**
- **Database:** ✅ Schema exists
  - `onboarding_tokens` table
  - Onboarding stage fields added (migration `20260122_0001_add_onboarding_stage_fields.py`)
- **Gap:** Frontend needs to be refactored into proper Pass pattern.

---

### 1.3 What is MISSING ❌

#### **A. Employee Request Passes**
**Requirement:** Passes for probation ending, visa/medical renewals, document expirations, etc.

**Current Situation:**
- **Database:** ✅ Fields exist in `employees` and `employee_compliance` tables:
  - `probation_start_date`, `probation_end_date`, `probation_status`
  - `visa_expiry_date`, `emirates_id_expiry`, `medical_fitness_expiry`
  - `contract_end_date`, `iloe_expiry`
- **Backend Routes:** ❌ No Pass endpoints for employee requests
- **Frontend:** ❌ No Pass components for employee requests
- **Workflow:** ❌ No defined stages/statuses for:
  - Probation review process
  - Visa renewal process
  - Medical fitness renewal process
  - Document renewal process

**Gap Analysis:**
These are **critical HR workflows** in UAE context but currently only exist as:
- Data fields in employee profile
- Compliance alerts dashboard (shows expirations)
- **No interactive employee-facing Pass system**

#### **B. Labor Law Quote Validation System**
**Requirement:** Show validated labor law quotes in Passes for employee education.

**Current Situation:**
- **No model** for storing law quotes
- **No admin interface** for validating quotes
- **No display mechanism** in Pass components
- **No quote database** (Article numbers, English/Arabic, source references)

**Gap Analysis:**
This is a **unique value-add** feature that would:
- Educate employees about their rights
- Reduce HR questions
- Build trust through transparency
- **Requires careful implementation to avoid misinterpretation**

#### **C. Employee Access Challenge**
**Requirement:** Employees need to access Passes without full portal login.

**Current Situation:**
- **Recruitment Passes:** ✅ Token-based access (works)
  - Candidate Pass: `/api/interview/pass/candidate/{id}`
  - Manager Pass: `/api/interview/pass/manager/{id}`
  - Nomination Pass: Token verification flow
- **Onboarding Pass:** ✅ Token-based access (backend ready)
  - `/onboarding/{token}` URL pattern
- **Employee Request Passes:** ❌ No token system yet

**Options Evaluated:**
1. **WhatsApp Bot** (mentioned by user)
2. **Email Magic Links** (existing pattern)
3. **SMS Links** (UAE-friendly)
4. **Employee Portal Login** (full HRIS)
5. **Hybrid: Pass Inbox** (curated links)

---

## 2. ARCHITECTURE PROPOSALS

### 2.1 Pass Interlinking Enhancement

**Current Status:** ✅ Already working for Manager ↔ Candidate via `InterviewSlot`.

**Proposed Enhancement:** Extend interlinking pattern to other Pass types.

#### **Pattern: Shared State Models**
```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Manager Pass   │────────▶│  InterviewSlot   │◀────────│ Candidate Pass  │
│                 │         │   (Shared State) │         │                 │
│  - Add slots    │         │  - slot_date     │         │  - View slots   │
│  - See bookings │         │  - booked_by     │         │  - Book slot    │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

**Apply Pattern To:**

1. **HR Pass ↔ Employee Pass (Onboarding)**
   - Shared State: `OnboardingChecklist`
   - HR updates checklist items → Employee sees progress
   - Employee completes tasks → HR sees completion

2. **HR Pass ↔ Employee Pass (Probation Review)**
   - Shared State: `ProbationReview`
   - HR schedules review → Employee sees scheduled date
   - Employee submits self-assessment → HR sees submission
   - Manager submits evaluation → Employee sees outcome

3. **HR Pass ↔ Employee Pass (Visa Renewal)**
   - Shared State: `RenewalRequest`
   - Employee submits documents → HR sees submission
   - HR updates status → Employee sees progress
   - System sends alerts → Both see notifications

**Implementation:**
```python
# backend/app/models/employee_pass.py (NEW)
class EmployeePassSharedState(Base):
    """Shared state model for employee pass interlinking."""
    __tablename__ = "employee_pass_shared_state"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    pass_type: Mapped[str] = mapped_column(String(50))  # probation, visa_renewal, onboarding
    state_data: Mapped[dict] = mapped_column(JSON)  # Flexible state storage
    last_updated_by: Mapped[str] = mapped_column(String(50))
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

**Benefits:**
- ✅ Real-time sync between HR and Employee views
- ✅ Single source of truth
- ✅ Audit trail of state changes
- ✅ Reuses proven pattern from recruitment

---

### 2.2 Employee Access Solution

#### **Recommended Approach: Hybrid Pass Inbox**

**Why NOT WhatsApp Bot (yet):**
- ❌ Requires WhatsApp Business API integration (~$1000-2000 setup + monthly fees)
- ❌ Complex compliance (data storage, GDPR/UAE data laws)
- ❌ Dependency on third-party service availability
- ❌ Difficult to audit message history
- ⚠️ **Risk:** Over-engineering before validating employee engagement

**Why NOT Full Employee Portal:**
- ❌ Requires authentication infrastructure
- ❌ Increases support burden (password resets, 2FA, etc.)
- ❌ Higher maintenance overhead
- ⚠️ Scope creep from simple Pass system

**Proposed Solution: Pass Inbox**

```
┌────────────────────────────────────────────────────────┐
│            EMPLOYEE PASS INBOX (Public URL)           │
│  URL: https://hrportal.com/my-passes/{employee_token} │
├────────────────────────────────────────────────────────┤
│  Welcome back, Ahmed Al-Mansoori!                     │
│                                                        │
│  📬 Your Active Passes (3)                             │
│  ┌──────────────────────────────────────────────┐     │
│  │ 🟢 Probation Review                          │     │
│  │    Review scheduled: Feb 15, 2025            │     │
│  │    [Open Pass →]                             │     │
│  └──────────────────────────────────────────────┘     │
│  ┌──────────────────────────────────────────────┐     │
│  │ 🟡 Visa Renewal                              │     │
│  │    Expiry in 45 days - Documents pending     │     │
│  │    [Open Pass →]                             │     │
│  └──────────────────────────────────────────────┘     │
│  ┌──────────────────────────────────────────────┐     │
│  │ ⚪ Medical Fitness Renewal                   │     │
│  │    Upcoming - Scheduled for March 2025       │     │
│  │    [Open Pass →]                             │     │
│  └──────────────────────────────────────────────┘     │
│                                                        │
│  📋 Completed Passes (2)                               │
│  - Onboarding Pass (Completed Jan 2024)              │
│  - Annual Leave Request #2024-042                     │
└────────────────────────────────────────────────────────┘
```

**Architecture:**

```
┌─────────────┐     Email/SMS      ┌──────────────────┐
│    HR       │──────────────────▶ │    Employee      │
│  (Creates   │   Magic Link       │                  │
│   Pass)     │                    │  Click link →    │
└─────────────┘                    │  Pass Inbox      │
                                   └──────────────────┘
                                            │
                                            ▼
                                   ┌──────────────────┐
                                   │  Individual Pass │
                                   │  (BasePass UI)   │
                                   │  - Timeline      │
                                   │  - Actions       │
                                   │  - Documents     │
                                   └──────────────────┘
```

**Implementation Steps:**

1. **Employee Token System**
   ```python
   # backend/app/models/employee_token.py (NEW)
   class EmployeeAccessToken(Base):
       """Long-lived token for employee Pass Inbox access."""
       __tablename__ = "employee_access_tokens"
       
       id: Mapped[int] = mapped_column(primary_key=True)
       employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
       token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
       expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # NULL = never expires
       is_active: Mapped[bool] = mapped_column(Boolean, default=True)
       created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
       last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
   ```

2. **Pass Inbox API**
   ```python
   # backend/app/routers/employee_pass.py (NEW)
   @router.get("/my-passes/{token}", response_model=EmployeePassInbox)
   async def get_employee_pass_inbox(
       token: str,
       session: AsyncSession = Depends(get_session)
   ):
       """Get employee's Pass Inbox (public endpoint)."""
       # Validate token
       employee = await validate_employee_token(session, token)
       if not employee:
           raise HTTPException(status_code=401, detail="Invalid access token")
       
       # Get all active passes for employee
       passes = await get_employee_active_passes(session, employee.id)
       
       return EmployeePassInbox(
           employee_name=employee.name,
           employee_id=employee.employee_id,
           active_passes=passes,
           completed_passes=await get_employee_completed_passes(session, employee.id)
       )
   ```

3. **Pass Inbox UI** (`frontend/src/components/EmployeePassInbox/`)
   - List view of active passes
   - Click to open individual Pass (uses BasePass components)
   - No login required (token-based)
   - Mobile-first design

**Benefits:**
- ✅ **Simple:** Single URL per employee (bookmark-able)
- ✅ **Secure:** 64-char random token, employee-scoped
- ✅ **No passwords:** Magic link via email/SMS
- ✅ **Audit trail:** Track access times
- ✅ **Scalable:** Add new Pass types without changing architecture
- ✅ **UAE-friendly:** Works with any device
- ✅ **Offline-capable:** Email/SMS delivery doesn't require internet

**Migration Path to WhatsApp (Future):**
Once validated, WhatsApp bot becomes a **notification channel** only:
```
HR creates Pass → System sends WhatsApp message with link → Employee clicks → Pass Inbox
```
Bot just delivers the link, actual Pass interaction happens in web UI (proven, controlled).

---

### 2.3 Labor Law Quote System

#### **Proposed Architecture**

**Goal:** Show validated labor law quotes in Passes without creating legal liability.

**Key Principles:**
1. **Admin-only validation** — Only HR admins can approve quotes
2. **Source attribution** — Every quote must cite article number + law
3. **Bilingual support** — Arabic + English (Arabic is authoritative)
4. **Context-aware display** — Show quotes relevant to Pass stage
5. **Disclaimer always shown** — "Not legal advice" notice

**Database Schema:**

```python
# backend/app/models/labor_law_quote.py (NEW)
class LaborLawQuote(Base):
    """Curated labor law quotes for employee education."""
    __tablename__ = "labor_law_quotes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    quote_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    
    # Content
    quote_english: Mapped[str] = mapped_column(Text, nullable=False)
    quote_arabic: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[str] = mapped_column(Text)  # Plain language explanation
    
    # Source attribution
    law_name: Mapped[str] = mapped_column(String(200))  # e.g., "Federal Decree-Law No. 33 of 2021"
    article_number: Mapped[str] = mapped_column(String(50))  # e.g., "Art. 42(1)"
    official_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Categorization
    category: Mapped[str] = mapped_column(String(100))  # probation, working_hours, leave, termination, etc.
    relevant_pass_types: Mapped[list] = mapped_column(JSON)  # ["probation_review", "visa_renewal"]
    relevant_stages: Mapped[list] = mapped_column(JSON)  # ["initiated", "pending_documents"]
    
    # Validation
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, pending_review, approved, archived
    submitted_by: Mapped[str] = mapped_column(String(50))
    approved_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class LaborLawQuoteRevision(Base):
    """Revision history for labor law quotes."""
    __tablename__ = "labor_law_quote_revisions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("labor_law_quotes.id"))
    revision_number: Mapped[int] = mapped_column(Integer)
    
    # Snapshot of quote at revision
    quote_snapshot: Mapped[dict] = mapped_column(JSON)
    
    # Change tracking
    changed_by: Mapped[str] = mapped_column(String(50))
    change_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

**Admin UI Flow:**

```
1. HR Admin creates quote
   ├─ Enter English text
   ├─ Enter Arabic text (optional but encouraged)
   ├─ Add plain language summary
   ├─ Cite law + article number
   ├─ Add official URL
   ├─ Tag categories
   └─ Submit for approval

2. HR Admin/Supervisor reviews
   ├─ Verify accuracy
   ├─ Check source citation
   ├─ Test context relevance
   └─ Approve or reject

3. Approved quote appears in Passes
   └─ Shows in relevant Pass types/stages only
```

**Display in Pass:**

```typescript
// frontend/src/components/BasePass/LaborLawQuote.tsx (NEW)
interface LaborLawQuoteProps {
  quote: {
    quote_english: string
    quote_arabic?: string
    summary: string
    law_name: string
    article_number: string
    official_url?: string
  }
}

export function LaborLawQuote({ quote }: LaborLawQuoteProps) {
  return (
    <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg mb-4">
      {/* Icon */}
      <div className="flex items-start gap-3">
        <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        
        <div className="flex-1">
          {/* Summary (plain language) */}
          <p className="text-sm font-medium text-blue-900 mb-2">
            {quote.summary}
          </p>
          
          {/* Quote (legal text) */}
          <blockquote className="text-xs text-blue-800 italic border-l-2 border-blue-300 pl-3 mb-2">
            "{quote.quote_english}"
          </blockquote>
          
          {/* Arabic version (if available) */}
          {quote.quote_arabic && (
            <blockquote className="text-xs text-blue-800 italic border-l-2 border-blue-300 pl-3 mb-2" dir="rtl">
              "{quote.quote_arabic}"
            </blockquote>
          )}
          
          {/* Source citation */}
          <div className="text-xs text-blue-700">
            <span className="font-semibold">Source:</span> {quote.law_name}, {quote.article_number}
            {quote.official_url && (
              <a href={quote.official_url} target="_blank" rel="noopener noreferrer" className="ml-2 underline hover:text-blue-900">
                View Official Source ↗
              </a>
            )}
          </div>
          
          {/* Disclaimer */}
          <p className="text-xs text-blue-600 mt-2 pt-2 border-t border-blue-200">
            <strong>Note:</strong> This is for informational purposes only and does not constitute legal advice. 
            For specific questions, please contact HR.
          </p>
        </div>
      </div>
    </div>
  )
}
```

**Example Quotes (UAE Private Sector):**

| Category | Quote | Law & Article |
|----------|-------|---------------|
| **Probation** | "Probationary period shall not exceed six months from the date of employment, unless a longer period is specified in the contract." | Federal Decree-Law No. 33 of 2021, Art. 10 |
| **Working Hours** | "Working hours shall not exceed eight hours per day or 48 hours per week." | Federal Decree-Law No. 33 of 2021, Art. 17 |
| **Overtime** | "The total number of overtime hours shall not exceed two hours per day, except in exceptional circumstances." | Federal Decree-Law No. 33 of 2021, Art. 18 |
| **Annual Leave** | "Employee is entitled to not less than 30 days of annual leave for each year of service after completing one year of continuous employment." | Federal Decree-Law No. 33 of 2021, Art. 29 |
| **Sick Leave** | "Employee is entitled to sick leave not exceeding 90 days per year, with the first 15 days fully paid, next 30 days half paid, and remaining days unpaid." | Federal Decree-Law No. 33 of 2021, Art. 31 |

**Integration with Passes:**

1. **Probation Review Pass** → Shows probation period quote + evaluation process quote
2. **Visa Renewal Pass** → Shows document requirements + timeline obligations
3. **Onboarding Pass** → Shows trial period rights + benefits
4. **Annual Leave Request Pass** → Shows entitlement calculation + notice periods

**API Integration:**

```python
# backend/app/routers/labor_law.py (NEW)
@router.get("/quotes", response_model=List[LaborLawQuoteResponse])
async def get_approved_quotes(
    category: Optional[str] = None,
    pass_type: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """Get approved labor law quotes (public endpoint)."""
    query = select(LaborLawQuote).where(LaborLawQuote.status == "approved")
    
    if category:
        query = query.where(LaborLawQuote.category == category)
    if pass_type:
        query = query.where(LaborLawQuote.relevant_pass_types.contains([pass_type]))
    
    result = await session.execute(query)
    return result.scalars().all()
```

**Benefits:**
- ✅ **Educates employees** about UAE labor law
- ✅ **Reduces HR questions** (self-service learning)
- ✅ **Builds trust** through transparency
- ✅ **Audit-defensible** (admin approval + source citation)
- ✅ **Bilingual support** for diverse workforce
- ✅ **Version controlled** (revision history)

**Risks & Mitigations:**
- ⚠️ **Risk:** Misinterpretation leading to disputes
  - **Mitigation:** Always show disclaimer, link to official source
- ⚠️ **Risk:** Outdated quotes after law changes
  - **Mitigation:** Annual review process, expiry dates
- ⚠️ **Risk:** Quote used in legal proceedings
  - **Mitigation:** Clear "not legal advice" language, watermark

---

## 3. EMPLOYEE REQUEST PASSES — Detailed Design

### 3.1 Probation Review Pass

**Purpose:** Guide employee and manager through probation evaluation process.

**Journey Stages:**
1. **Initiated** (60 days before probation end)
2. **Self-Assessment** (Employee completes)
3. **Manager Review** (Manager evaluates)
4. **HR Review** (HR validates)
5. **Decision** (Confirmation or termination)

**Pass Data Structure:**

```typescript
interface ProbationReviewPassData {
  // Pass info
  pass_id: string
  pass_token: string
  
  // Employee info
  employee_id: string
  employee_name: string
  department: string
  job_title: string
  probation_start: string
  probation_end: string
  days_remaining: number
  
  // Current stage
  current_stage: 'initiated' | 'self_assessment' | 'manager_review' | 'hr_review' | 'decision'
  status: string
  
  // Self-assessment
  self_assessment_submitted: boolean
  self_assessment_date?: string
  self_assessment_data?: {
    achievements: string
    challenges: string
    goals: string
    feedback_request: string
  }
  
  // Manager evaluation
  manager_evaluation_submitted: boolean
  manager_evaluation_date?: string
  manager_evaluation_data?: {
    performance_rating: number
    strengths: string
    areas_for_improvement: string
    recommendation: 'confirm' | 'extend' | 'terminate'
  }
  
  // HR decision
  hr_decision?: 'confirmed' | 'extended' | 'terminated'
  hr_decision_date?: string
  hr_notes?: string
  
  // Labor law quote
  labor_law_quotes: LaborLawQuote[]
  
  // Activity history
  activity_history: ActivityItem[]
}
```

**UI Flow (Employee View):**

```
┌─────────────────────────────────────────────────────────┐
│  PROBATION REVIEW PASS                                 │
│  Employee: Ahmed Al-Mansoori                           │
│  Probation Period: Jan 1 - Jun 30, 2025               │
├─────────────────────────────────────────────────────────┤
│  Timeline:                                             │
│  ● Initiated → ● Self-Assessment → ○ Manager Review   │
│                   → ○ HR Review → ○ Decision           │
├─────────────────────────────────────────────────────────┤
│  📋 Next Action:                                        │
│  Complete Self-Assessment (Due: May 15, 2025)         │
│  [Start Assessment →]                                  │
├─────────────────────────────────────────────────────────┤
│  📚 What You Should Know:                              │
│  ┌───────────────────────────────────────────────┐    │
│  │ Probation Period Rights                       │    │
│  │ "Probationary period shall not exceed six     │    │
│  │  months from the date of employment..."       │    │
│  │ Source: UAE Labour Law, Art. 10               │    │
│  └───────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

### 3.2 Visa Renewal Pass

**Purpose:** Track visa renewal process from initiation to completion.

**Journey Stages:**
1. **Alert Issued** (60 days before expiry)
2. **Documents Pending** (Employee submits documents)
3. **HR Processing** (HR validates + submits to authorities)
4. **Authority Processing** (GDRFA/Immigration)
5. **Completed** (New visa issued)

**Pass Data Structure:**

```typescript
interface VisaRenewalPassData {
  pass_id: string
  pass_token: string
  
  // Employee info
  employee_id: string
  employee_name: string
  nationality: string
  current_visa_number: string
  current_visa_expiry: string
  days_until_expiry: number
  
  // Current stage
  current_stage: 'alert_issued' | 'documents_pending' | 'hr_processing' | 'authority_processing' | 'completed'
  status: string
  
  // Required documents
  required_documents: Array<{
    document_type: string
    is_submitted: boolean
    submitted_date?: string
    status: 'pending' | 'submitted' | 'approved' | 'rejected'
    rejection_reason?: string
  }>
  
  // Processing info
  application_number?: string
  submission_date?: string
  estimated_completion?: string
  
  // New visa info
  new_visa_number?: string
  new_visa_expiry?: string
  
  // Labor law quotes
  labor_law_quotes: LaborLawQuote[]
  
  // Activity history
  activity_history: ActivityItem[]
}
```

**Required Documents (UAE Standard):**
- Valid passport copy
- Emirates ID copy
- Recent photo (white background)
- Employment contract
- Labor card copy
- Current visa copy
- Medical fitness certificate (if applicable)

**UI Flow (Employee View):**

```
┌─────────────────────────────────────────────────────────┐
│  VISA RENEWAL PASS                                     │
│  Employee: Ahmed Al-Mansoori                           │
│  Current Visa Expiry: March 15, 2025 (45 days left)   │
├─────────────────────────────────────────────────────────┤
│  Timeline:                                             │
│  ● Alert → ● Documents → ○ HR Processing               │
│           → ○ Authority → ○ Completed                  │
├─────────────────────────────────────────────────────────┤
│  📋 Next Action:                                        │
│  Upload Required Documents (3 pending)                 │
│  [Upload Documents →]                                  │
├─────────────────────────────────────────────────────────┤
│  📄 Document Checklist:                                │
│  ✅ Valid Passport Copy (Uploaded Jan 20)             │
│  ✅ Emirates ID Copy (Uploaded Jan 20)                │
│  ❌ Recent Photo (Pending)                             │
│  ❌ Medical Fitness Certificate (Pending)              │
│  ❌ Current Visa Copy (Pending)                        │
├─────────────────────────────────────────────────────────┤
│  📚 Important Information:                             │
│  ┌───────────────────────────────────────────────┐    │
│  │ Visa Renewal Timeline                         │    │
│  │ Processing typically takes 2-3 weeks after    │    │
│  │ all documents are submitted. Ensure your      │    │
│  │ documents are uploaded at least 30 days       │    │
│  │ before expiry to avoid penalties.             │    │
│  └───────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

### 3.3 Medical Fitness Renewal Pass

Similar structure to Visa Renewal Pass, with stages:
1. **Alert Issued** (45 days before expiry)
2. **Appointment Scheduled** (Employee books medical)
3. **Medical Completed** (Test results pending)
4. **HR Processing** (Certificate submission)
5. **Completed** (New certificate issued)

---

### 3.4 Document Expiration Passes

Generic pass for:
- Emirates ID renewal
- Passport renewal
- Labor card renewal
- Insurance card renewal
- Driving license renewal (if company vehicle)

**Trigger:** Automated creation 60 days before document expiry (from `employee_compliance` table).

---

## 4. IMPLEMENTATION ROADMAP

### Phase 1: Foundation (2-3 weeks)

**Goal:** Complete Onboarding Pass and establish Employee Pass architecture.

**Tasks:**
1. **Refactor Onboarding Frontend**
   - Create `OnboardingPass.tsx` using BasePass components
   - Add journey timeline (5 stages)
   - Add action tracking
   - Add document upload interface
   - Add labor law quote display placeholder

2. **Employee Token System**
   - Create `EmployeeAccessToken` model
   - Create token generation endpoint
   - Create token validation middleware

3. **Pass Inbox UI**
   - Create `EmployeePassInbox` component
   - List active passes
   - List completed passes
   - Navigate to individual passes

**Deliverables:**
- ✅ Onboarding Pass (complete frontend)
- ✅ Employee Pass Inbox (basic version)
- ✅ Token system (working)

---

### Phase 2: Employee Request Passes (3-4 weeks)

**Goal:** Implement Probation Review and Visa Renewal Passes.

**Tasks:**
1. **Probation Review Pass**
   - Create backend models (`ProbationReview`)
   - Create API endpoints
   - Create frontend component
   - Integrate with HR dashboard
   - Add automated alerts (60 days before end)

2. **Visa Renewal Pass**
   - Create backend models (`VisaRenewal`)
   - Create API endpoints
   - Create frontend component
   - Integrate document upload
   - Add automated alerts (60 days before expiry)

3. **Medical Fitness Renewal Pass**
   - Create backend models (`MedicalRenewal`)
   - Create API endpoints
   - Create frontend component
   - Add automated alerts (45 days before expiry)

**Deliverables:**
- ✅ 3 new employee request Pass types
- ✅ Automated alert system
- ✅ Document upload integration

---

### Phase 3: Labor Law Quote System (2 weeks)

**Goal:** Build admin interface for labor law quote management.

**Tasks:**
1. **Backend Models**
   - Create `LaborLawQuote` model
   - Create `LaborLawQuoteRevision` model
   - Create API endpoints

2. **Admin UI**
   - Create quote submission form
   - Create quote approval workflow
   - Create quote library view
   - Add search/filter

3. **Pass Integration**
   - Add `LaborLawQuote` component
   - Integrate into all Pass types
   - Context-aware quote display

4. **Seed Data**
   - Add 10-15 initial quotes for UAE private sector
   - Categories: probation, working hours, leave, termination
   - Sources: Federal Decree-Law No. 33 of 2021 + Cabinet Resolution No. 1 of 2022

**Deliverables:**
- ✅ Labor law quote admin system
- ✅ Quote display in all Passes
- ✅ Initial quote library (UAE-focused)

---

### Phase 4: Enhancement & Optimization (2-3 weeks)

**Goal:** Polish UX, add analytics, prepare for scale.

**Tasks:**
1. **Analytics**
   - Track Pass open rates
   - Track action completion rates
   - Track time-to-completion by Pass type

2. **Notifications**
   - Email notifications for Pass updates
   - SMS notifications (optional)
   - WhatsApp notification preparation (infrastructure only)

3. **Mobile Optimization**
   - Test all Passes on mobile devices
   - Optimize touch targets
   - Add PWA support (install as app)

4. **Performance**
   - Add caching for Pass data
   - Optimize database queries
   - Add loading states

**Deliverables:**
- ✅ Analytics dashboard
- ✅ Notification system
- ✅ Mobile-optimized UX
- ✅ Performance improvements

---

### Phase 5: WhatsApp Integration (Future, Optional)

**Prerequisites:**
- Phase 1-4 complete
- Employee Pass Inbox validated (usage metrics)
- Budget approved for WhatsApp Business API

**Approach:**
WhatsApp becomes **notification channel only**, not primary interface:
1. HR creates Pass → System sends WhatsApp message
2. Message contains: "New Visa Renewal Pass created. [Open Pass]"
3. Link opens Pass Inbox (web UI)
4. All interaction happens in Pass Inbox (proven, controlled)

**Benefits of This Approach:**
- ✅ No need to build complex WhatsApp bot
- ✅ WhatsApp is just notification (like email)
- ✅ Pass UI remains consistent
- ✅ Easier to maintain
- ✅ Lower cost

---

## 5. TECHNICAL SPECIFICATIONS

### 5.1 Database Migrations Required

**New Tables:**

1. `employee_access_tokens` — Long-lived tokens for Pass Inbox
2. `employee_pass_shared_state` — Interlinking state (generic)
3. `probation_reviews` — Probation review workflow
4. `visa_renewals` — Visa renewal tracking
5. `medical_renewals` — Medical fitness renewal tracking
6. `document_renewals` — Generic document renewal tracking
7. `labor_law_quotes` — Curated law quotes
8. `labor_law_quote_revisions` — Quote version history

**Modified Tables:**
- `passes` — Add `employee_pass_type` column

**Indexes:**
- `employee_access_tokens.token` (unique)
- `employee_pass_shared_state.employee_id + pass_type`
- `labor_law_quotes.status + category`

---

### 5.2 API Endpoints Required

**Employee Pass Inbox:**
```
GET  /api/my-passes/{token}                    # Get Pass Inbox
GET  /api/my-passes/{token}/pass/{pass_id}     # Get individual Pass
POST /api/my-passes/{token}/pass/{pass_id}/action  # Perform action
```

**Probation Review:**
```
GET  /api/employee-pass/probation/{employee_id}        # Get probation Pass
POST /api/employee-pass/probation/{employee_id}/self-assessment  # Submit self-assessment
POST /api/employee-pass/probation/{employee_id}/manager-evaluation  # Submit manager evaluation
POST /api/employee-pass/probation/{employee_id}/decision  # HR decision
```

**Visa Renewal:**
```
GET  /api/employee-pass/visa/{employee_id}             # Get visa Pass
POST /api/employee-pass/visa/{employee_id}/documents   # Upload documents
GET  /api/employee-pass/visa/{employee_id}/status      # Get renewal status
```

**Labor Law Quotes:**
```
GET  /api/labor-law/quotes                             # Get approved quotes (public)
GET  /api/labor-law/quotes/admin                       # Get all quotes (admin)
POST /api/labor-law/quotes                             # Create quote (admin)
PUT  /api/labor-law/quotes/{id}/approve                # Approve quote (admin)
GET  /api/labor-law/quotes/{id}/revisions              # Get revision history
```

---

### 5.3 Frontend Components Required

**New Components:**

1. **EmployeePassInbox/** (Root component for Pass Inbox)
   - `PassInboxContainer.tsx` — Main inbox UI
   - `PassCard.tsx` — Individual Pass card
   - `PassFilter.tsx` — Filter by type/status

2. **OnboardingPass/** (Refactor from App.tsx)
   - `OnboardingPass.tsx` — Full Pass UI using BasePass
   - `OnboardingChecklist.tsx` — Task checklist
   - `OnboardingDocuments.tsx` — Document upload

3. **ProbationReviewPass/**
   - `ProbationReviewPass.tsx` — Main Pass component
   - `SelfAssessmentForm.tsx` — Employee self-assessment
   - `ManagerEvaluationForm.tsx` — Manager evaluation
   - `DecisionView.tsx` — Final decision display

4. **VisaRenewalPass/**
   - `VisaRenewalPass.tsx` — Main Pass component
   - `DocumentUploader.tsx` — Multi-document upload
   - `RenewalTimeline.tsx` — Process timeline

5. **LaborLawQuote/** (Shared component)
   - `LaborLawQuote.tsx` — Quote display
   - `LaborLawQuoteAdmin.tsx` — Admin management

**Component Reuse:**
- All new Passes use `BasePassContainer`, `JourneyTimeline`, `ActionRequired`, `ActivityHistory`
- Consistent UX across all Pass types

---

### 5.4 Security Considerations

**Employee Access Tokens:**
- ✅ 64-character random tokens (URL-safe)
- ✅ Scoped to employee_id (cannot access other employees' data)
- ✅ Optional expiry (default: no expiry for long-term inbox access)
- ✅ Can be revoked (set `is_active = false`)
- ✅ Rate-limited to prevent abuse

**Pass Data Exposure:**
- ✅ Only show data relevant to Pass holder (employee vs HR)
- ✅ Mask sensitive data (salary, bank details) unless necessary
- ✅ Activity history shows only public-facing events to employees

**Document Upload:**
- ✅ File type validation (PDF, JPEG, PNG only)
- ✅ File size limits (5MB per file)
- ✅ Virus scanning (ClamAV or Azure Defender)
- ✅ Secure storage (Azure Blob Storage with private access)

**Labor Law Quotes:**
- ✅ Admin-only creation/approval
- ✅ Public read access (no authentication)
- ✅ Version history preserved
- ✅ Disclaimer always shown

---

## 6. UAE COMPLIANCE SUMMARY

### 6.1 Probation Review Pass

**UAE Labor Law Reference:**
- **Article 10** (Probation Period): Max 6 months, can terminate without notice/indemnity
- **Article 115** (Employment Records): Employer must maintain employment records

**Compliance Features:**
- ✅ Tracks probation period (start/end dates)
- ✅ Ensures review before end of probation
- ✅ Documents evaluation (audit trail)
- ✅ Notifies employee of rights

---

### 6.2 Visa Renewal Pass

**UAE Immigration Requirements:**
- Visa renewal must be completed before expiry
- Employer responsible for renewal process
- Late renewal penalties apply

**Compliance Features:**
- ✅ Alerts 60 days before expiry
- ✅ Tracks document submission
- ✅ Maintains audit trail
- ✅ Prevents last-minute renewals

---

### 6.3 Medical Fitness Renewal Pass

**UAE Requirements:**
- Medical fitness required for visa/labor card
- Renewal required periodically (employer-specific)
- Specific medical centers authorized

**Compliance Features:**
- ✅ Alerts before expiry
- ✅ Tracks medical appointment
- ✅ Stores certificate securely
- ✅ Audit trail for compliance

---

### 6.4 Labor Law Quote System

**Legal Disclaimer Required:**
All quotes must include:

> "This information is provided for general guidance only and does not constitute legal advice. 
> Labor law interpretation may vary based on specific circumstances. For specific questions 
> regarding your employment rights or obligations, please consult with HR or a qualified 
> legal professional. Arabic version is authoritative in case of discrepancy."

**Source Requirements:**
- ✅ Cite Federal Decree-Law No. 33 of 2021 (UAE Labour Law)
- ✅ Cite Cabinet Resolution No. 1 of 2022 (Executive Regulations)
- ✅ Cite Ministerial Decisions where applicable
- ✅ Include article numbers
- ✅ Link to official MOHRE sources

---

## 7. RISKS & MITIGATIONS

### Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Employees ignore Passes (low adoption)** | Medium | High | Send email/SMS notifications, make Inbox easy to access |
| **Labor law quotes misinterpreted** | Medium | High | Always show disclaimer, link to official source, admin approval |
| **Token security breach** | Low | High | Use long random tokens, rate limiting, revocation capability |
| **Outdated law quotes after legislation changes** | Medium | Medium | Annual review process, expiry dates, admin alerts |
| **WhatsApp integration cost overrun** | Low | Medium | Phase 5 is optional, validate need first via Pass Inbox metrics |
| **Performance issues with many Passes** | Low | Medium | Pagination, caching, database indexing |
| **Employee doesn't receive Pass link** | Medium | Low | Fallback to multiple channels (email + SMS), HR can resend |
| **Pass interlinking state conflicts** | Low | High | Use database transactions, optimistic locking, audit trail |

---

## 8. SUCCESS METRICS

### Phase 1-2 (Foundation + Employee Requests)
- ✅ **90%+ Pass open rate** (employees click link within 48 hours)
- ✅ **80%+ action completion rate** (employees complete required actions)
- ✅ **50%+ reduction in HR follow-up emails/calls**
- ✅ **<5 sec Pass load time** (on mobile 4G)

### Phase 3 (Labor Law Quotes)
- ✅ **15+ approved quotes** in library (covering major categories)
- ✅ **Quotes displayed in 100% of relevant Passes**
- ✅ **Zero legal complaints** related to quote misinterpretation

### Phase 4-5 (Enhancement + WhatsApp)
- ✅ **Pass Inbox bookmarked** by 70%+ of employees
- ✅ **Time-to-completion** reduced by 30% vs manual process
- ✅ **Employee satisfaction** score >4/5 for Pass system

---

## 9. QUESTIONS FOR SUPERVISOR

Before proceeding with implementation, please clarify:

1. **Priority Order:**
   - Which Pass type should be built first: Onboarding, Probation Review, or Visa Renewal?
   - Can we postpone WhatsApp integration to Phase 5 (after validating Pass Inbox)?

2. **Labor Law Quotes:**
   - Do you want to start with 10-15 quotes, or build the admin system first and add quotes later?
   - Should quotes be bilingual (Arabic + English) or English-only initially?
   - Who will be the quote approver(s)?

3. **Employee Access:**
   - Confirm: Pass Inbox approach is acceptable (vs full employee portal)?
   - Should employee tokens expire, or remain active indefinitely?
   - SMS notifications: Required or optional?

4. **Scope Control:**
   - Should we limit Phase 1-2 to just Onboarding + Probation Review (defer Visa/Medical)?
   - Any other Pass types needed urgently (Annual Leave, Ticket Requests, etc.)?

5. **Resources:**
   - Timeline expectations: Is 10-12 weeks (Phases 1-4) acceptable?
   - Budget for SMS gateway (if required)?

---

## 10. CONCLUSION

The Pass system architecture is **fundamentally sound**. Manager Pass and Candidate Pass demonstrate the pattern works well. The gaps are:

1. **Onboarding Pass** — Backend exists, needs frontend refactor (1 week)
2. **Employee Request Passes** — New build required (3-4 weeks)
3. **Labor Law Quotes** — Admin system + integration (2 weeks)
4. **Employee Access** — Pass Inbox is the pragmatic solution (avoids WhatsApp complexity upfront)

**Recommended Action:**
- ✅ **Approve Pass Inbox approach** (simpler, faster, proven pattern)
- ✅ **Start with Phase 1** (Onboarding Pass + Pass Inbox foundation)
- ✅ **Build Probation Review Pass in Phase 2** (highest UAE compliance value)
- ✅ **Defer WhatsApp to Phase 5** (validate need via metrics first)

This approach delivers **maximum value with minimum risk**, staying true to HR Harem's principles:
- **Calm:** Simple Pass Inbox, no password complexity
- **Intentional:** Purpose-built for each workflow
- **Compliance-first:** UAE labor law at the core
- **HR-controlled:** Admin approval for sensitive content
- **Scalable:** Pattern proven, ready to extend

---

**End of Document**

*For questions or clarifications, escalate to Supervisor.*
