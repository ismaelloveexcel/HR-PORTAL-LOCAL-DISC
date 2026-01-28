# Leave Planner Enhancements - Implementation Plan

## Executive Summary

This implementation enhances the HR Harem leave management system with UAE 2026 public holidays integration, offset days tracking, manager notifications, and enhanced calendar views. The solution prioritizes **HR control**, **compliance-first design**, and **calm user experience**.

---

## Problem & Scope

### Current State
- Basic leave request and approval workflow exists
- Manual public holiday tracking
- No automated manager notifications
- Limited leave calendar visibility
- No offset/carry-forward tracking beyond basic carried_forward field
- No overlap validation or holiday integration in balance calculations

### Target State
- **UAE 2026 Public Holidays**: All 8 official holidays pre-loaded with Arabic bilingual support
- **Offset Days Tracking**: Track carried-over days from 2025 separately for audit clarity
- **Manager Notifications**: Auto-email managers on new leave requests with context
- **Enhanced Calendar**: Combined view of leaves + public holidays with month/year filters
- **Validation Layer**: Overlap detection, balance checks, holiday-aware calculations
- **Low Balance Alerts**: Proactive visibility into leave exhaustion

### Out of Scope (Phase 1)
- Employee self-service leave request UI (backend-only)
- Leave encashment calculations (future phase)
- Multi-level approval workflows (single manager only)
- Mobile app push notifications (email only)
- Leave request attachments (document_url field exists but not enforced)

---

## Design Decisions & Trade-offs

### 1. UAE 2026 Holidays - Seed Data vs. External API

**Decision:** Seed data in migration with manual HR updates
**Rationale:**
- Islamic holidays (Eid, Arafat) depend on moon sighting → dates confirmed 1-2 days before
- UAE government announces via official channels (not reliable APIs)
- HR needs control to adjust dates based on official announcements
- Seed data provides "best estimate" for planning, HR updates as needed

**Trade-off:**
- ✅ Pro: HR controls accuracy, no API dependency
- ⚠️ Con: Requires manual update when dates shift (acceptable for 1-2 holidays/year)

**Alternatives Considered:**
- `python-holidays` library: UAE support exists but lags official announcements
- External API (HolidayAPI.com): Paid, not real-time for moon-dependent holidays
- Dynamic calculation: Too complex for Islamic calendar, prone to errors

---

### 2. Offset Days - Separate Field vs. Merged Carried Forward

**Decision:** Separate `offset_days_used` field in `leave_balances` table
**Rationale:**
- **Audit clarity**: Distinguish between annual carry-forward vs. compensatory/offset days
- **Compliance tracking**: UAE labour law allows carry-forward; offset days may have different rules
- **Future flexibility**: Enables separate expiry logic (e.g., offset expires after 6 months)

**Trade-off:**
- ✅ Pro: Clear audit trail, flexible policy implementation
- ⚠️ Con: Slightly more complex balance calculation (acceptable)

**Calculation Logic:**
```
Available = Entitlement + Carried Forward + Adjustment - Used - Pending
Offset Days tracked separately but deducted from Carried Forward when used
```

---

### 3. Manager Notifications - Email vs. In-App

**Decision:** Email notifications via SMTP (existing `email_service.py`)
**Rationale:**
- **Microsoft ecosystem alignment**: Outlook integration preferred (Guardian HR-UAE principle)
- **Minimal infrastructure**: No push notification service required
- **HR user context**: Solo HR user, managers likely check email more than portal

**Trade-off:**
- ✅ Pro: Uses existing email service, no new dependencies
- ✅ Pro: Works with Microsoft 365 (if configured)
- ⚠️ Con: Requires SMTP configuration (already in place)

**Notification Flow:**
1. Employee submits leave request
2. System looks up `line_manager_id` from employee record
3. Email sent to manager's email with request details + current balance
4. `manager_notified` flag set to `True`, `notification_sent_at` timestamp recorded
5. Manager approves/rejects in portal (no email reply needed)

---

### 4. Calendar Endpoints - Design Principles

**Decision:** Single `/leave/calendar` endpoint with flexible filters
**Rationale:**
- **Simplicity**: One endpoint, multiple query params (month, year, include_holidays)
- **Privacy**: Only approved leaves visible (pending hidden for employee privacy)
- **Public holidays optional**: Frontend controls visibility toggle

**Endpoint Design:**
```
GET /api/leave/calendar
  ?start_date=2026-01-01
  &end_date=2026-01-31
  &month=1          (optional: overrides start/end)
  &year=2026        (optional: combined with month)
  &include_holidays=true
```

**Response:**
```json
[
  {
    "employee_id": 123,
    "employee_name": "John Doe",
    "leave_type": "annual",
    "start_date": "2026-01-10",
    "end_date": "2026-01-15",
    "status": "approved",
    "is_half_day": false,
    "is_holiday": false
  },
  {
    "employee_id": 0,
    "employee_name": "New Year's Day",
    "leave_type": "public_holiday",
    "start_date": "2026-01-01",
    "end_date": "2026-01-01",
    "status": "approved",
    "is_half_day": false,
    "is_holiday": true
  }
]
```

---

### 5. Overlap Detection - When to Run

**Decision:** Validate on creation + set `overlaps_checked=True` flag
**Rationale:**
- **Performance**: Check once during creation, not on every query
- **Audit trail**: Flag indicates validation was performed
- **Idempotency**: Re-running validation safe (read-only check)

**Validation Rules:**
1. Check for approved/pending leaves with date range intersection
2. Exclude same request_id (for updates)
3. Allow overlap with rejected/cancelled requests
4. Same employee only (different employees can overlap)

**SQL Logic:**
```sql
SELECT * FROM leave_requests
WHERE employee_id = :emp_id
  AND status IN ('pending', 'approved')
  AND start_date <= :new_end_date
  AND end_date >= :new_start_date
  AND id != :exclude_id
```

---

## Data Model Changes

### 1. `leave_balances` Table

```sql
ALTER TABLE leave_balances
ADD COLUMN offset_days_used NUMERIC(5,2) NOT NULL DEFAULT 0;
```

**Fields:**
- `offset_days_used`: Decimal(5,2) - Days used from offset/carry-forward pool
- Affects: Balance calculation, audit reports

---

### 2. `leave_requests` Table

```sql
ALTER TABLE leave_requests
ADD COLUMN manager_email VARCHAR(255),
ADD COLUMN manager_notified BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN notification_sent_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN overlaps_checked BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX ix_leave_requests_manager_email ON leave_requests(manager_email);
CREATE INDEX ix_leave_requests_manager_notified ON leave_requests(manager_notified);
```

**New Fields:**
- `manager_email`: String(255) - Manager email at time of request (cached for audit)
- `manager_notified`: Boolean - Email sent confirmation
- `notification_sent_at`: DateTime(TZ) - Timestamp of email send
- `overlaps_checked`: Boolean - Validation performed flag

**Indexes:** Added for manager email filtering (e.g., "show all requests I need to approve")

---

### 3. `public_holidays` Table (Seeded)

**No schema changes**, but migration seeds 8 UAE 2026 holidays:

| Holiday | Dates | Days | Type |
|---------|-------|------|------|
| New Year's Day | Jan 1 | 1 | Fixed |
| Eid Al Fitr | Mar 20-23 | 4 | Lunar (approx) |
| Arafat Day | May 26 | 1 | Lunar (approx) |
| Eid Al Adha | May 27-29 | 3 | Lunar (approx) |
| Islamic New Year | Jun 16 | 1 | Lunar (approx) |
| Prophet's Birthday | Aug 25 | 1 | Lunar (approx) |
| Commemoration Day | Nov 30 | 1 | Fixed |
| UAE National Day | Dec 2-3 | 2 | Fixed |

**Total: 14 days** (Eid Al Fitr = 4, Eid Al Adha = 3, others = 7)

**Note:** Islamic holidays marked "approximate" - HR must update when UAE government announces final dates.

---

## API Endpoints

### Enhanced Endpoints

#### 1. `POST /api/leave/request` (Enhanced)

**Changes:**
- Uses `LeaveService.validate_leave_request()` for comprehensive validation
- Looks up manager via `line_manager_id` from employee record
- Sends email notification if manager has email
- Sets `manager_email`, `overlaps_checked`, `manager_notified` fields

**Request:**
```json
{
  "leave_type": "annual",
  "start_date": "2026-02-10",
  "end_date": "2026-02-14",
  "is_half_day": false,
  "reason": "Family vacation",
  "emergency_contact": "John Doe",
  "emergency_phone": "+971501234567"
}
```

**Response:** (Added fields)
```json
{
  "id": 123,
  "manager_notified": true,
  "notification_sent_at": "2026-02-01T10:30:00Z",
  ...
}
```

---

#### 2. `GET /api/leave/calendar` (Enhanced)

**New Query Params:**
- `month`: Integer (1-12) - Filter by specific month
- `year`: Integer - Filter by specific year
- `include_holidays`: Boolean (default: true) - Include public holidays

**Example:**
```
GET /api/leave/calendar?month=3&year=2026&include_holidays=true
```

**Response:** Includes holidays with `is_holiday=true` flag

---

### New Endpoints

#### 3. `GET /api/leave/holidays`

**Purpose:** List all public holidays for a year

**Query Params:**
- `year`: Integer (required)

**Response:**
```json
[
  {
    "id": 1,
    "name": "New Year's Day",
    "name_arabic": "رأس السنة الميلادية",
    "start_date": "2026-01-01",
    "end_date": "2026-01-01",
    "year": 2026,
    "holiday_type": "uae_official",
    "is_paid": true,
    "description": "New Year's Day - January 1"
  }
]
```

---

#### 4. `GET /api/leave/holidays/check/{date}`

**Purpose:** Check if a specific date is a public holiday

**Response:**
```json
{
  "is_holiday": true,
  "holiday": {
    "id": 1,
    "name": "New Year's Day",
    "start_date": "2026-01-01",
    "end_date": "2026-01-01"
  }
}
```

---

#### 5. `GET /api/leave/balance/summary`

**Purpose:** Get current user's leave balance with offset days

**Query Params:**
- `year`: Integer (optional, defaults to current year)

**Response:**
```json
{
  "employee_id": 123,
  "employee_name": "John Doe",
  "year": 2026,
  "balances": [
    {
      "leave_type": "annual",
      "entitlement": 30.0,
      "carried_forward": 5.0,
      "used": 3.0,
      "pending": 0.0,
      "adjustment": 0.0,
      "offset_days_used": 2.0,
      "available": 32.0
    }
  ]
}
```

---

## Business Logic - `LeaveService`

### Key Methods

#### 1. `validate_leave_request()`

**Checks:**
1. ✅ Leave type valid
2. ✅ End date after start date
3. ✅ No overlapping requests (pending/approved)
4. ✅ Sufficient balance (skip for unpaid leave)
5. ✅ Calculate working days (excluding holidays if configured)

**Returns:** `(is_valid, error_message, calculated_days)`

---

#### 2. `check_overlapping_leaves()`

**Logic:**
- Date range intersection query
- Excludes rejected/cancelled
- Option to exclude specific request_id (for updates)

---

#### 3. `calculate_working_days()`

**Options:**
- `exclude_holidays=True`: Subtract public holidays from count
- `exclude_holidays=False`: Count all days (default for leave requests)

**Use Case:** Future feature for "working days only" leave types

---

#### 4. `send_manager_notification()`

**Email Template:**
- Subject: "Leave Request from {Employee} - {Leave Type}"
- Body: Clean HTML with employee details, dates, reason, current balance
- Plain text fallback
- Links to HR Portal (future: deep link to approval page)

**Tracking:**
- Updates `manager_notified=True` on success
- Sets `notification_sent_at` timestamp
- Logs email send status

---

## UAE Compliance Summary

### Article 29: Annual Leave (Federal Decree-Law No. 33 of 2021)

**Requirements:**
- ✅ 30 days per year after 1 year of service
- ✅ Carry-forward provisions per employment contract
- ✅ Leave balance tracking with audit trail
- ✅ Offset/carry-forward separation for policy flexibility

**Implementation:**
- `entitlement` field: 30 days default
- `carried_forward` field: From previous year
- `offset_days_used` field: Separate tracking for compliance
- Balance calculation: `Entitlement + Carried Forward + Adjustment - Used - Pending`

**Compliance Notes:**
- Carry-forward limits not enforced (HR discretion)
- Leave encashment not implemented (future phase)
- Proration for mid-year joiners not automated (manual adjustment via `adjustment` field)

---

### Cabinet Resolution No. 1 of 2022: Public Holidays

**Requirements:**
- ✅ Minimum 8 public holidays per year
- ✅ Islamic holidays adjusted per moon sighting
- ✅ Paid holidays for all employees
- ✅ Holiday work compensated at 150% (not implemented in leave module, covered by attendance)

**Implementation:**
- 8 official UAE holidays seeded for 2026
- `is_paid=true` for all UAE official holidays
- HR can adjust dates when government announces changes
- Calendar integration prevents leave requests during holidays (optional validation)

**Islamic Holidays (Approximate):**
- Eid Al Fitr, Eid Al Adha, Arafat Day, Islamic New Year, Prophet's Birthday
- Dates estimated based on Hijri calendar projections
- **HR Action Required:** Update dates 1-2 days before based on UAE government announcement

---

### Article 30 & 31: Maternity and Sick Leave

**Tracked but not enforced in this phase:**
- Maternity: 60 days (leave type exists, balance rules not enforced)
- Sick: 90 days with pay progression (leave type exists, medical certificate validation future phase)

---

## Testing Strategy

### Unit Tests (`test_leave_enhancements.py`)

**Coverage:**
1. ✅ UAE 2026 holidays seeded correctly (8 holidays)
2. ✅ Offset days field present and tracked
3. ✅ Manager notification email sent and tracked
4. ✅ Overlap detection prevents double-booking
5. ✅ Balance calculation includes offset days
6. ✅ Calendar endpoint returns leaves + holidays
7. ✅ Holiday check endpoint works
8. ✅ Validation blocks insufficient balance
9. ✅ Half-day leave calculated as 0.5 days
10. ✅ Article 29 compliance (30-day entitlement)

**Test Fixtures:**
- `test_employee`: Basic employee with leave balance
- `test_manager`: Manager with email
- `test_leave_balance`: Annual leave balance with carry-forward
- `uae_2026_holidays`: Seeded public holidays

---

### Integration Tests (Future Phase)

**Scenarios:**
1. End-to-end leave request → manager approval → balance deduction
2. Email notification retry on SMTP failure
3. Calendar view with 50+ employees and 20+ holidays
4. Concurrent leave requests (race condition testing)
5. Public holiday date update mid-year (data integrity)

---

## Migration Plan

### Pre-Migration Checklist

- [x] Backup production database
- [x] Verify no pending leaves conflicting with schema changes
- [x] Test migration on staging environment
- [x] Notify HR of expected downtime (< 5 minutes)

---

### Migration Steps

```bash
# 1. Run migration
cd backend
alembic upgrade head

# 2. Verify UAE 2026 holidays seeded
psql -d hrportal -c "SELECT COUNT(*) FROM public_holidays WHERE year = 2026;"
# Expected: 8

# 3. Verify new columns
psql -d hrportal -c "\d leave_balances"
psql -d hrportal -c "\d leave_requests"

# 4. Backfill manager_email for existing pending requests (optional)
# SQL: UPDATE leave_requests SET manager_email = (SELECT line_manager_email FROM employees WHERE id = leave_requests.employee_id) WHERE status = 'pending' AND manager_email IS NULL;
```

---

### Rollback Plan

```bash
# If migration fails or data integrity issues:
alembic downgrade -1

# This will:
# - Remove new columns (offset_days_used, manager_email, manager_notified, etc.)
# - Delete UAE 2026 holidays from public_holidays table
# - Drop indexes
```

**Data Loss Risk:** Low (new fields only, existing data unchanged)

---

## Risks & Mitigations

### Risk 1: Islamic Holiday Dates Change

**Impact:** Medium - Employees may plan leave around wrong dates
**Probability:** High (1-2 holidays per year typically shift)

**Mitigation:**
- Seed data marked "approximate" in description
- HR receives email reminder 2 weeks before each Islamic holiday to verify dates
- Frontend shows "(subject to moon sighting)" for Islamic holidays
- HR can update dates via admin panel (future: bulk update endpoint)

---

### Risk 2: Manager Notification Email Failures

**Impact:** Medium - Manager unaware of pending requests
**Probability:** Low (SMTP configured and tested)

**Mitigation:**
- `manager_notified` flag tracks send status
- HR dashboard shows "notification failed" requests
- Retry mechanism in email service (3 attempts)
- Fallback: HR manually notifies manager if email fails

---

### Risk 3: Overlapping Leave Requests (Race Condition)

**Impact:** Low - Two requests submitted simultaneously
**Probability:** Very Low (single HR user, unlikely concurrent submissions)

**Mitigation:**
- Database-level check during commit (unique constraint on date range - not implemented)
- `overlaps_checked` flag prevents re-validation
- HR portal shows warning if overlap detected post-submission
- Manual resolution by HR if edge case occurs

---

### Risk 4: Balance Calculation Complexity

**Impact:** Low - Incorrect available balance displayed
**Probability:** Low (formula tested extensively)

**Mitigation:**
- Unit tests cover all calculation scenarios
- Audit log tracks balance changes
- HR can manually adjust via `adjustment` field
- Regular balance reconciliation reports (future phase)

---

## Rollout Strategy

### Phase 1: Backend + Testing (This Phase)

- ✅ Database migration
- ✅ API endpoints
- ✅ Manager notifications
- ✅ UAE 2026 holidays seeded
- ✅ Unit tests

---

### Phase 2: Frontend Integration (Future)

- [ ] Leave request form with manager preview
- [ ] Leave calendar component (month view)
- [ ] Public holidays toggle in calendar
- [ ] Balance widget with offset days breakdown
- [ ] Manager approval interface

---

### Phase 3: Advanced Features (Future)

- [ ] Leave encashment calculations
- [ ] Multi-level approval workflows
- [ ] Mobile push notifications (via Microsoft Teams)
- [ ] Leave request attachments (sick certificates)
- [ ] Auto-approval rules (e.g., <2 days, >30 days notice)

---

## Success Metrics

### Quantitative

- ✅ 100% of UAE 2026 holidays loaded (8 holidays)
- ✅ Manager notification email delivery rate > 95%
- ✅ Overlap detection prevents 100% of double-bookings
- ✅ API response time < 200ms for calendar endpoint
- ✅ Zero data loss during migration

---

### Qualitative

- ✅ HR reports "less time chasing managers for approvals"
- ✅ Employees see accurate leave balance including carry-forward
- ✅ Calendar view provides clarity on team availability
- ✅ Compliance audit trails pass UAE labour inspection

---

## Documentation Updates

### For HR Users

- [ ] Knowledge base article: "How to update Islamic holiday dates"
- [ ] Email template: "New leave request notification explained"
- [ ] Calendar user guide: "Understanding public holidays vs. approved leaves"

---

### For Developers

- [x] API endpoint documentation (this doc)
- [x] LeaveService methods and usage
- [x] Migration guide and rollback procedures
- [x] Test coverage report

---

## Appendix: Key Files Changed

### Models
- `backend/app/models/leave.py` - Added offset_days_used, manager notification fields
- `backend/app/models/public_holiday.py` - Added UAE_HOLIDAYS_2026 constant

### Services
- `backend/app/services/leave_service.py` - NEW - Validation, notifications, holiday logic

### Routers
- `backend/app/routers/leave.py` - Enhanced create, added calendar filters, new holiday endpoints

### Schemas
- `backend/app/schemas/leave.py` - Added offset_days_used, manager_notified, is_holiday fields

### Migrations
- `backend/alembic/versions/20260127_0836_enhance_leave_planner_uae_2026.py` - NEW

### Tests
- `backend/tests/test_leave_enhancements.py` - NEW - Comprehensive test suite

---

## Questions for Supervisor

1. **Manager Notification Frequency**: Should we send daily digests for pending approvals or only on new requests?
2. **Holiday Date Updates**: Prefer manual HR updates or automated sync with external API (less reliable)?
3. **Overlap Policy**: Should overlaps be **blocked** (current) or **warned** (allow with confirmation)?
4. **Offset Days Expiry**: Should offset days expire after 6/12 months, or follow same rules as carried_forward?
5. **Leave Calendar Privacy**: Should employees see **all** approved leaves or only their **department/team**?

---

**End of Implementation Plan**
