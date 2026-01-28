# Leave Planner Quick Reference Card

## For HR Users

### What's New in This Release

✅ **UAE 2026 Public Holidays** - All 8 official holidays pre-loaded
✅ **Manager Notifications** - Auto-email managers when employees request leave
✅ **Enhanced Calendar** - See leaves and holidays together
✅ **Offset Days Tracking** - Separate tracking for carried-over days
✅ **Smart Validation** - Prevents overlapping leave requests

---

## UAE 2026 Public Holidays (Pre-loaded)

| Holiday | Date(s) | Days |
|---------|---------|------|
| New Year's Day | Jan 1 | 1 |
| Eid Al Fitr | Mar 20-23 | 4 |
| Arafat Day | May 26 | 1 |
| Eid Al Adha | May 27-29 | 3 |
| Islamic New Year | Jun 16 | 1 |
| Prophet's Birthday | Aug 25 | 1 |
| Commemoration Day | Nov 30 | 1 |
| UAE National Day | Dec 2-3 | 2 |
| **TOTAL** | - | **14 days** |

⚠️ **Islamic holidays are approximate** - Update when government announces official dates

---

## How It Works

### When Employee Submits Leave Request

1. **System validates:**
   - No overlapping requests
   - Sufficient leave balance
   - Valid dates

2. **Manager gets email:**
   - Employee name and department
   - Leave dates and type
   - Current balance
   - Reason provided

3. **Status tracked:**
   - `manager_notified` = True
   - Email sent timestamp recorded

---

## New API Endpoints

### Get UAE Holidays
```
GET /api/leave/holidays?year=2026
```

### Check if Date is Holiday
```
GET /api/leave/holidays/check/2026-01-01
```
Returns: `{ "is_holiday": true, "holiday": {...} }`

### Get Leave Calendar with Holidays
```
GET /api/leave/calendar?month=3&year=2026&include_holidays=true
```

### Get Employee Balance with Offset Days
```
GET /api/leave/balance/summary?year=2026
```

---

## Leave Balance Calculation

**Formula:**
```
Available = Entitlement + Carried Forward + Adjustment - Used - Pending
```

**Example:**
- Entitlement: 30 days (Article 29)
- Carried Forward: 5 days (from 2025)
- Used: 3 days (already taken)
- Pending: 2 days (approved but not started)
- **Available: 30 days**

**Offset Days:** Tracked separately in `offset_days_used` field

---

## Manager Notification Email Template

**Subject:** Leave Request from {Employee} - {Leave Type}

**Body includes:**
- Employee name and department
- Leave type (Annual, Sick, etc.)
- Start and end dates
- Duration (days)
- Current balance
- Reason (if provided)

**Action Required:** Manager logs into portal to approve/reject

---

## What HR Needs to Do

### 1. Update Islamic Holiday Dates (When Announced)

**When:** 1-2 days before Eid/Arafat/Islamic New Year
**How:** Admin panel → Public Holidays → Edit holiday dates
**Why:** Moon sighting determines exact dates

### 2. Configure SMTP (If Not Done)

**Required for manager notifications:**
- SMTP host: Outlook/Microsoft 365 preferred
- From email: `hr@baynunah.ae`
- Username and password

**Check:** Settings → Email Configuration

### 3. Monitor Notification Failures

**Dashboard shows:**
- Requests with `manager_notified = False`
- Email send errors

**Action:** Manually notify manager if email fails

---

## Validation Rules

### Overlap Prevention
❌ **Blocked:** Two leave requests with overlapping dates
✅ **Allowed:** Different employees, same dates

### Balance Check
❌ **Blocked:** Request exceeds available balance
✅ **Allowed:** Unpaid leave (no balance check)

### Date Validation
❌ **Blocked:** End date before start date
✅ **Allowed:** Same-day leave (half-day)

---

## Troubleshooting

### Manager Not Getting Emails

**Check:**
1. Manager has email in employee record?
2. SMTP configured in settings?
3. Email service logs show errors?

**Fix:** Update manager email or resend notification

### Wrong Holiday Dates

**Check:**
1. Is it an Islamic holiday (moon-dependent)?
2. Has UAE government announced final date?

**Fix:** Edit holiday in admin panel

### Employee Can't Request Leave (Balance Error)

**Check:**
1. View balance: Entitlement - Used - Pending
2. Check offset days used
3. Review adjustments

**Fix:** Adjust balance if needed (with reason)

---

## UAE Compliance Checklist

- [x] 30 days annual leave entitlement (Article 29)
- [x] Carry-forward up to 30 days supported
- [x] 8 public holidays minimum (Cabinet Resolution 1/2022)
- [x] Manager approval required (no auto-approval)
- [x] Audit trail for all actions
- [x] Bilingual holiday names (Arabic + English)

---

## Quick Commands

### Check Migration Status
```bash
cd backend
alembic current
```

### Seed Holidays Manually (If Needed)
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

---

## Data Fields Reference

### Leave Request
- `manager_email` - Cached at request time
- `manager_notified` - Email sent? (true/false)
- `notification_sent_at` - When email sent
- `overlaps_checked` - Validated? (true/false)

### Leave Balance
- `offset_days_used` - Carried-over days used
- `available` - Calculated: Entitlement + Carried - Used - Pending

---

## Support Contacts

**Technical Issues:** DevOps team
**Policy Questions:** HR Manager
**Compliance Queries:** Legal team or MOHRE

---

## Next Phase Features (Future)

- [ ] Leave encashment calculator
- [ ] Multi-level approval workflows
- [ ] Mobile app notifications
- [ ] Document attachments (sick certificates)
- [ ] Auto-approval rules (e.g., < 2 days)

---

**Last Updated:** January 27, 2026
**Version:** 1.0.0
**Documentation:** See LEAVE_PLANNER_PLAN.md for full details
