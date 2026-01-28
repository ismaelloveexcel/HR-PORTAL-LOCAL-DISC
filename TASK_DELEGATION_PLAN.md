# Task Delegation Plan
## Agent Assignment for HR Portal Enhancement

**Created:** January 27, 2026  
**Purpose:** Identify appropriate agents and delegate tasks for implementation

---

## 🎯 Available Custom Agents

Based on repository analysis, the following custom agents are available:

### 1. **portal-engineer** (Primary Implementation Agent)
**Capabilities:** Full-stack development, database migrations, API implementation  
**Tools:** All CLI tools, Sonnet model  
**Best for:** Feature implementation, bug fixes, urgent tasks

### 2. **guardian-hr-uae** (HR Compliance & UAE Law Expert)
**Capabilities:** UAE private-sector HR compliance, labour law citations, ESS features  
**Tools:** Domain expertise in UAE Federal Decree-Law 33/2021  
**Best for:** Compliance features, legal requirements, UAE-specific implementations

### 3. **hr-portal-finalizer** (MVP Completion Specialist)
**Capabilities:** Owns Azure deployment MVP, pragmatic fast delivery, user-first approach  
**Tools:** Blueprint-guided implementation with logic and common sense  
**Best for:** Finalizing MVP features, deployment readiness, practical solutions

### 4. **oss-scout** (Research & Module Discovery)
**Capabilities:** GitHub research, open-source module evaluation, pattern discovery  
**Tools:** GitHub search, comparison, adaptation to UAE context  
**Best for:** Finding existing solutions, evaluating libraries, research tasks

---

## 📋 Task Delegation Matrix

### PHASE 1: Urgent Features (1-Hour Execution Plan)

#### Task 1: Recruitment Process Completion
**Assigned to:** `portal-engineer`  
**Reason:** Full-stack capability, backend + API implementation  
**Estimated time:** 10 minutes  
**Deliverables:**
- Bulk candidate operations (move stage, reject)
- Recruitment metrics dashboard API
- Offer letter generation support
- Pipeline visualization endpoints

**Validation:** Test bulk operations via Swagger UI

---

#### Task 2: Employee Database Enhancement + Bulk Import
**Assigned to:** `portal-engineer`  
**Reason:** Database operations, CSV/Excel parsing, validation logic  
**Estimated time:** 10 minutes  
**Deliverables:**
- Enhanced CSV export with all fields
- Bulk update capability
- Import preview endpoint
- Column mapping support
- Error report generation

**Validation:** Import 10-row test CSV, verify validation

---

#### Task 3: Leave Planner Enhancement (UAE Compliance)
**Assigned to:** `guardian-hr-uae` (PRIMARY) + `portal-engineer` (SUPPORT)  
**Reason:** UAE public holidays, offset days per labour law, compliance-critical  
**Estimated time:** 20 minutes  
**Deliverables:**
- Public holidays model (UAE 2026 - 11 holidays)
- Offset days tracking (carried over per UAE law)
- Manager email notifications
- Calendar visualization endpoints
- Overlap detection + validation

**Reference:** https://github.com/ismaelloveexcel/employee-leave-plann

**Validation:** Test with UAE 2026 holidays, verify balance calculation

**Delegation command:**
```bash
# Delegate to guardian-hr-uae
Use the "task" tool with agent_type="guardian-hr-uae"
Prompt: "Implement leave planner enhancements with UAE 2026 public holidays (11 holidays), offset days tracking per UAE labour law, manager notifications, and calendar endpoints. Reference: https://github.com/ismaelloveexcel/employee-leave-plann for UX patterns. Ensure compliance with Federal Decree-Law 33/2021 annual leave provisions. Backend implementation in backend/app/routers/leave.py, backend/app/models/public_holiday.py."
```

---

#### Task 4: Performance Appraisal Completion
**Assigned to:** `portal-engineer`  
**Reason:** Standard CRUD operations, workflow implementation  
**Estimated time:** 20 minutes  
**Deliverables:**
- Review submission workflow
- Rating calculation logic
- Performance reports generation
- Reminder system for review cycles

**Validation:** Complete review cycle end-to-end

---

### PHASE 2: Critical Automation (Weeks 1-4)

#### Task 5: Compliance Dashboard & Automated Alerts
**Assigned to:** `guardian-hr-uae`  
**Reason:** UAE compliance requirements, legal deadline tracking  
**Estimated time:** 1 week  
**Deliverables:**
- Compliance dashboard UI (HR-only)
- Automated alerts (30/60/90 days before expiry)
- Email notification templates
- Visa, EID, medical fitness, ILOE tracking
- Excel export functionality

**UAE Compliance Articles:**
- Federal Decree-Law 33/2021: Work permits, visa requirements
- Cabinet Resolution 1/2022: Document requirements

**Validation:** Test with dummy data expiring in 30/60/90 days

**Delegation command:**
```bash
Use agent_type="guardian-hr-uae"
Prompt: "Build compliance dashboard with automated alerts for visa, Emirates ID, medical fitness, and ILOE expiry. Alert windows: 30/60/90 days before expiry. Include email templates citing relevant UAE Federal Decree-Law 33/2021 articles. Dashboard should be HR-only with color-coded alerts (red/orange/green). Include CSV export for compliance reports. Implement APScheduler for daily cron job."
```

---

#### Task 6: Document Auto-Generation Service
**Assigned to:** `portal-engineer`  
**Reason:** PDF generation, template merging, file handling  
**Estimated time:** 1 week  
**Deliverables:**
- PDF generation service (WeasyPrint or ReportLab)
- Salary certificate template + auto-fill
- Employment letter template + auto-fill
- NOC template + auto-fill
- Template merge with employee data
- HR review + approval workflow

**Validation:** Generate all 3 document types, verify data accuracy

---

#### Task 7: Bulk Compliance Data Import
**Assigned to:** `guardian-hr-uae` (PRIMARY) + `portal-engineer` (SUPPORT)  
**Reason:** UAE compliance data validation, legal date tracking  
**Estimated time:** 2 days  
**Deliverables:**
- Compliance data bulk import endpoint
- CSV format: visa, EID, medical, contract dates
- Validation per UAE requirements
- Error report with compliance gaps
- Automatic expiry flagging

**CSV Format:**
```csv
employee_id,visa_number,visa_expiry_date,eid_number,eid_expiry,medical_expiry,contract_start,contract_end
EMP001,123456,2027-01-15,784-1234-5678901-2,2026-12-31,2026-06-30,2024-01-01,2026-12-31
```

**Validation:** Import 60 employee records, verify compliance flags

**Delegation command:**
```bash
Use agent_type="guardian-hr-uae"
Prompt: "Implement bulk compliance data import for visa, Emirates ID, medical fitness, and contract dates. Support CSV/Excel import for 60+ employees. Validate data per UAE Federal Decree-Law 33/2021 requirements. Auto-flag expired documents. Include error report with missing/invalid data. Endpoint: POST /api/employee_compliance/import. Time estimate: 2 days."
```

---

#### Task 8: Leave Balance Automation
**Assigned to:** `guardian-hr-uae`  
**Reason:** UAE annual leave entitlement calculations  
**Estimated time:** 3 days  
**Deliverables:**
- Automatic monthly leave accrual (per UAE law)
- Auto-deduction on leave approval
- Balance notification system
- Carry-forward calculation (offset days)
- Low balance alerts

**UAE Compliance:**
- Federal Decree-Law 33/2021, Article 29: Annual leave entitlement (30 days/year for 1+ year service)
- Carry-forward provisions per employment contract

**Validation:** Test accrual for 12 months, verify balance calculations

---

#### Task 9: Attendance Reminders
**Assigned to:** `portal-engineer`  
**Reason:** Simple scheduled task implementation  
**Estimated time:** 2 days  
**Deliverables:**
- Clock-in reminder at 9 AM
- Clock-out reminder at 6 PM
- WhatsApp integration (optional)
- Missing attendance follow-up
- HR dashboard for missing clock-ins

**Validation:** Test reminder delivery, verify no duplicates

---

### PHASE 3: Research & Module Discovery

#### Task 10: Evaluate Existing Solutions for Features
**Assigned to:** `oss-scout`  
**Reason:** Research specialist, GitHub module discovery  
**Estimated time:** Ongoing, as needed  
**Deliverables:**
- Identify open-source HR modules
- Compare options for specific features
- Adaptation recommendations for UAE context
- License compliance verification

**Example research tasks:**
- Find open-source PDF generation libraries
- Evaluate email notification services
- Research background task schedulers
- Identify calendar visualization libraries

**Delegation command:**
```bash
Use agent_type="oss-scout"
Prompt: "Research open-source solutions for [specific feature]. Requirements: [list requirements]. Must be compatible with Python/FastAPI backend. Evaluate licensing, maintenance, UAE context adaptation. Provide top 3 options with pros/cons."
```

---

### PHASE 4: MVP Finalization & Deployment

#### Task 11: Complete Azure Deployment MVP
**Assigned to:** `hr-portal-finalizer`  
**Reason:** Owns Azure deployment MVP, pragmatic approach  
**Estimated time:** As needed for deployment issues  
**Deliverables:**
- Azure App Service configuration
- Database migrations execution
- Environment variables setup
- Health checks post-deployment
- Troubleshooting deployment issues

**Validation:** Production health check passes

**Delegation command:**
```bash
Use agent_type="hr-portal-finalizer"
Prompt: "Finalize Azure deployment for HR portal MVP. Ensure all critical features are production-ready: recruitment, employee DB, leave planner, performance appraisal. Verify database migrations, environment variables, and health endpoints. Target: solo HR user with extreme workload. Pragmatic and fast delivery."
```

---

## 🚀 Execution Strategy

### Parallel Execution (Maximum Efficiency)

**Block 1 (0-20 min):**
- `portal-engineer` → Task 1 (Recruitment) + Task 2 (Employee DB)
- Execute in parallel using separate sessions

**Block 2 (20-40 min):**
- `guardian-hr-uae` → Task 3 (Leave Planner - UAE compliance critical)
- `portal-engineer` → Task 4 (Performance Appraisal)
- Execute in parallel

**Block 3 (40-50 min):**
- `portal-engineer` → Integration testing (all 4 features)

**Block 4 (50-60 min):**
- `portal-engineer` → Documentation + commit

### Sequential Execution (Week-by-Week)

**Week 1:**
- `guardian-hr-uae` → Task 5 (Compliance Dashboard)
- `portal-engineer` → Task 6 (Document Auto-Generation)

**Week 2:**
- `guardian-hr-uae` → Task 7 (Bulk Compliance Import)
- `portal-engineer` → Task 9 (Attendance Reminders)

**Week 3:**
- `guardian-hr-uae` → Task 8 (Leave Balance Automation)

**Week 4:**
- `portal-engineer` → Integration testing + deployment prep
- `hr-portal-finalizer` → Azure deployment finalization

---

## 📞 How to Delegate Tasks

### Using the Task Tool

For custom agents, use the `task` tool with appropriate `agent_type`:

```python
# Example: Delegate to guardian-hr-uae
task(
    agent_type="guardian-hr-uae",
    description="Compliance dashboard implementation",
    prompt="""
    Build compliance dashboard with automated alerts for UAE labour law compliance.
    
    Requirements:
    - Track visa, EID, medical fitness, ILOE expiry
    - Alert windows: 30/60/90 days
    - Email templates with UAE Federal Decree-Law 33/2021 citations
    - HR-only dashboard with color-coded alerts
    - CSV export for compliance reports
    - APScheduler for daily cron job
    
    Deliverables:
    - backend/app/routers/compliance_dashboard.py
    - backend/app/services/compliance_alerts.py
    - Email templates with legal citations
    - Alembic migration for any schema changes
    
    Timeline: 1 week
    """
)
```

### Task Assignment Checklist

Before delegating, ensure:
- [ ] Task scope is clear and specific
- [ ] Deliverables are well-defined
- [ ] Acceptance criteria are measurable
- [ ] Timeline is realistic
- [ ] Dependencies are identified
- [ ] Agent has required capabilities
- [ ] Reference materials are provided (if needed)

---

## 🎯 Agent Selection Decision Tree

```
Is the task UAE compliance-related?
├─ YES → Use `guardian-hr-uae`
│   └─ Examples: Leave law, visa tracking, compliance alerts
│
├─ NO → Is it MVP finalization or deployment?
    ├─ YES → Use `hr-portal-finalizer`
    │   └─ Examples: Azure deployment, production readiness
    │
    ├─ NO → Is it research or module discovery?
        ├─ YES → Use `oss-scout`
        │   └─ Examples: Library evaluation, pattern research
        │
        └─ NO → Use `portal-engineer`
            └─ Examples: Standard features, APIs, CRUD operations
```

---

## ✅ Success Criteria

### For Each Agent

**portal-engineer:**
- Code compiles without errors
- Tests pass (if applicable)
- API endpoints documented in Swagger
- Database migrations successful
- Code follows repository patterns

**guardian-hr-uae:**
- UAE compliance verified with article citations
- Legal requirements met per Federal Decree-Law 33/2021
- Compliance checklist included in PR description
- MOHRE/UAE sources linked

**hr-portal-finalizer:**
- MVP features fully functional
- Azure deployment successful
- Health checks pass
- User-tested for solo HR workflow
- Documentation updated

**oss-scout:**
- Top 3 options provided with analysis
- Licensing verified
- UAE adaptation notes included
- Recommendation rationale clear

---

## 📊 Task Tracking

| Task # | Feature | Agent | Status | ETA | Dependencies |
|--------|---------|-------|--------|-----|--------------|
| 1 | Recruitment completion | portal-engineer | 🔴 Not started | 10 min | None |
| 2 | Employee DB + bulk import | portal-engineer | 🔴 Not started | 10 min | None |
| 3 | Leave planner (UAE) | guardian-hr-uae | 🔴 Not started | 20 min | employee-leave-plann repo |
| 4 | Performance appraisal | portal-engineer | 🔴 Not started | 20 min | None |
| 5 | Compliance dashboard | guardian-hr-uae | 🔴 Not started | 1 week | Task 7 (import) |
| 6 | Document auto-gen | portal-engineer | 🔴 Not started | 1 week | None |
| 7 | Bulk compliance import | guardian-hr-uae | 🔴 Not started | 2 days | None |
| 8 | Leave balance automation | guardian-hr-uae | 🔴 Not started | 3 days | Task 3 (planner) |
| 9 | Attendance reminders | portal-engineer | 🔴 Not started | 2 days | None |
| 10 | Research (ongoing) | oss-scout | 🟡 As needed | Varies | Feature requests |
| 11 | MVP finalization | hr-portal-finalizer | 🔴 Not started | Varies | Tasks 1-4 |

---

## 🔄 Iteration & Feedback Loop

After each agent completes a task:

1. **Review Output** - Check deliverables against acceptance criteria
2. **Test Functionality** - Smoke test the implementation
3. **Update Status** - Mark task complete or identify issues
4. **Document Learnings** - Note any patterns or conventions discovered
5. **Plan Next Task** - Identify dependencies resolved, queue next task

---

## 📝 Notes for Solo HR

**You don't need to understand the technical details.** Just know:

- **For urgent tasks (< 1 hour):** Use `portal-engineer`
- **For UAE compliance features:** Use `guardian-hr-uae`
- **For final deployment:** Use `hr-portal-finalizer`
- **For finding solutions:** Use `oss-scout`

**To delegate a task:** Reply to this PR with:
> "@copilot delegate Task X to [agent-name]"

Example:
> "@copilot delegate Task 3 (Leave planner) to guardian-hr-uae"

---

**Document Version:** 1.0  
**Last Updated:** January 27, 2026  
**Next Review:** After first batch of tasks complete
