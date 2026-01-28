1. CORE IDENTITY & ACCESS (FOUNDATIONAL)
These features must exist before anything else.
•	Employee identity record (unique employee number)
•	Manager identity record
•	Candidate identity record
•	Role-based access:
o	Employee
o	Manager
o	HR
•	Language toggle (EN / AR)
•	Secure access to sensitive sections (payroll, personal data)
•	Session tracking (last login, unusual access flag)
________________________________________
2. EMPLOYEE MASTER & PROFILE MANAGEMENT
The system must be able to:
•	Store complete employee master data
•	Store personal details separately from HR-only data
•	Track profile completion %
•	Flag missing mandatory data
•	Allow HR-only edits on restricted fields
•	Store and manage:
o	Personal info
o	Emergency contacts
o	Bank details
o	Dependents
o	Documents (EID, passport, visa, contracts)
•	Maintain a change log for all manual edits
________________________________________
3. UAE COMPLIANCE & LEGAL TRACKING (NON-NEGOTIABLE)
The portal must automatically handle:
•	Visa tracking (issue date, expiry, alerts)
•	Emirates ID tracking
•	Medical fitness tracking
•	ILOE / insurance tracking
•	Contract tracking:
o	Start / end
o	Type
o	Renewal reminders
•	WPS readiness (bank IBAN capture & validation)
•	Compliance alerts:
o	60 / 30 / 7 days
•	HR-only compliance dashboard
•	Non-compliance flagging
•	Monthly compliance summary
(This is mandatory per UAE labour law exposure — see consolidated risk analysis 
COMPLETE_ANALYSIS_AND_ROADMAP
)
________________________________________
4. ATTENDANCE & WORK MODE MANAGEMENT
The system must support:
•	Daily clock in / clock out
•	Work location capture
•	Work modes:
o	Office
o	WFH
o	Client site
o	Business travel
•	Automatic reminders for:
o	Missing clock-in
o	Missing clock-out
•	Monthly timesheet (calendar view)
•	Manual correction requests
•	HR approval of corrections
•	Attendance non-compliance reporting
•	Overtime tracking
•	Offset day tracking
________________________________________
5. LEAVE MANAGEMENT
The portal must:
•	Display leave balances (by type)
•	Support leave requests
•	Route approvals (HR → Manager → Finance where applicable)
•	Validate balances
•	Enforce policy rules (carry forward, documentation)
•	Generate leave records automatically
•	Store leave history
•	Flag excessive leave / abuse patterns
•	Produce leave summaries for payroll
________________________________________
6. PAYROLL VISIBILITY (NOT PAYROLL ENGINE)
The system must:
•	Display salary structure (read-only for employees)
•	Show payslips
•	Track:
o	Deductions
o	Overtime payouts
o	Salary advances
•	Link attendance & leave to payroll inputs
•	Allow HR to trigger payslip availability
•	Maintain payslip history
(No salary calculations here — visibility & linkage only)
________________________________________
7. EMPLOYEE REQUESTS (SELF-SERVICE)
Employees must be able to request:
•	Leave
•	Salary certificate
•	Employment letter
•	Bank letter
•	NOC
•	Experience certificate
•	Reimbursements
•	Bank account update
•	Parking request
•	Grievance / complaint
•	General HR requests
System must:
•	Track status (Submitted → In Review → Approved → Completed)
•	Route approvals based on request type
•	Enforce documentation requirements
•	Prevent duplicate submissions
•	Maintain request history
•	Auto-notify status changes
________________________________________
8. DOCUMENT & POLICY MANAGEMENT
The portal must:
•	Store HR document templates
•	Store generated employee documents
•	Maintain document versioning
•	Provide policy library
•	Track policy acknowledgements
•	Send reminders for unacknowledged policies
•	Restrict sensitive documents to HR
•	Maintain audit trail
________________________________________
9. RECRUITMENT & ONBOARDING
The system must support:
Recruitment
•	Manager-initiated recruitment request (RRF)
•	Candidate database
•	Recruitment stages
•	Interview scheduling
•	Evaluation capture
•	Offer request & approvals
•	Candidate communication status
•	Recruitment metrics (time to hire, source)
Onboarding
•	Candidate document upload
•	HR verification
•	Conversion to employee record
•	Onboarding checklist tracking
•	Probation tracking
(Matches Recruitment Pass structure 
Updated blueprint 221125
)
________________________________________
10. MANAGER FEATURES
Managers must be able to:
•	View team members
•	Approve:
o	Leave
o	Requests
o	Corrections
•	View team attendance
•	View team compliance status (high level)
•	Submit recruitment requests
•	Submit interview evaluations
•	Add notes for HR
Managers do not see payroll, grievances, or HR-only data.
________________________________________
11. NOTIFICATIONS & REMINDERS
System-wide automated notifications for:
•	Attendance reminders
•	Approval pending
•	Approval completed
•	Document expiry
•	Policy acknowledgements
•	Payslip availability
•	Leave decisions
•	Missing information
•	Recruitment status updates
Delivery channels:
•	Email
•	WhatsApp (where enabled)
________________________________________
12. DASHBOARDS & REPORTING (ROLE-BASED)
HR Dashboard
•	Pending actions
•	Compliance status
•	Requests aging
•	Attendance exceptions
•	Document expiry
•	Recruitment pipeline
Manager Dashboard
•	Team attendance
•	Pending approvals
•	Team leave calendar
Employee View
•	Pending actions
•	Notifications
•	Status indicators
________________________________________
13. UNIVERSAL PASS (OVERLAY FEATURE)
The portal must generate:
•	Candidate Pass
•	Employee Pass
•	Manager Pass
Each pass must:
•	Show identity
•	Show timeline/status
•	Provide QR access to profile
•	Provide quick links to actions
•	Not replace the portal
•	Reflect live system data
(This is an experience layer, not a system of record — see Universal Pass spec 
THE UNIVERSAL PASS STRUCTURE
)
________________________________________
14. AUDIT, LOGGING & GOVERNANCE
Mandatory backend features:
•	Change logs
•	Approval logs
•	Data access control
•	Segregation of sensitive data
•	Historical record retention
•	HR-only override with justification





1. DEFINE THE SINGLE SOURCE OF TRUTH (START POINT)
Primary Anchor Record
The Employee Master Record is the spine of the entire system.
Every other module links to this. Nothing links sideways.
Non-negotiable anchor field:
•	Employee Number (unique, immutable)
This is the only field that:
•	never changes
•	never gets reused
•	never gets edited
Everything else can evolve.
________________________________________
2. MIGRATION STRATEGY (DO NOT DUMP EVERYTHING AT ONCE)
Rule
Migrate in layers, not in bulk
Why:
•	avoids corrupt links
•	avoids compliance gaps
•	avoids rework
________________________________________
3. LAYER 1 — CORE EMPLOYEE MASTER (MIGRATE FIRST)
This is what you migrate from your existing list immediately.
Employee Master – Core Fields
These must exist before anything else.
Category	Field
Identity	Employee Number
Identity	Full Name
Org	Job Title
Org	Department
Org	Line Manager
Employment	Employment Status
Employment	Date of Joining
Employment	Work Location
System	Employee Type (Employee / Manager)
Why this layer first
•	Enables linking
•	Enables permissions
•	Enables dashboards
•	Enables compliance mapping
❗ At this stage:
•	No documents
•	No bank details
•	No salary
•	No personal data
________________________________________
4. LAYER 2 — PERSONAL DETAILS (SEPARATE, LINKED)
Personal data must NOT live directly inside Employee Master.
Personal Details Table (Linked to Employee Master)
Link field:
•	Employee Number → Employee Master
Fields to migrate / collect here
Basic Personal
•	Date of Birth
•	Gender
•	Nationality
•	Personal Email
•	Personal Mobile
Emergency
•	Emergency Contact Name
•	Relationship
•	Contact Number
Family (if applicable)
•	Marital Status
•	Dependents (basic identifiers only)
❗Important:
•	This layer can be partially empty
•	Missing data is acceptable temporarily
•	Completion % will be tracked later
________________________________________
5. LAYER 3 — COMPLIANCE & LEGAL DATA (HR-ONLY)
This layer is critical for UAE risk control and must be isolated.
Compliance Table (Linked to Employee Master)
Link field:
•	Employee Number → Employee Master
Mandatory UAE Fields
Category	Field
Visa	Visa Number
Visa	Visa Issue Date
Visa	Visa Expiry Date
EID	Emirates ID Number
EID	Emirates ID Expiry
Medical	Medical Fitness Date
Medical	Medical Fitness Expiry
Insurance	ILOE Status
Insurance	ILOE Expiry
Contract	Contract Type
Contract	Contract Start
Contract	Contract End
Why separate
•	HR-only access
•	Audit readiness
•	Clean expiry logic
•	No accidental exposure
________________________________________
6. LAYER 4 — BANK & PAYROLL REFERENCE (RESTRICTED)
This is visibility + validation, not payroll processing.
Bank Details Table (Linked)
Link field:
•	Employee Number → Employee Master
Fields
•	Bank Name
•	IBAN
•	Account Holder Name
•	Effective Date
❗Key rule:
•	Employees can submit
•	HR validates
•	No direct overwrite
________________________________________
7. LAYER 5 — DOCUMENTS (DO NOT MIGRATE BLINDLY)
Documents should not be dumped.
Document Registry (Linked)
Link field:
•	Employee Number → Employee Master
Document Metadata (before files)
•	Document Type
•	Issue Date
•	Expiry Date
•	Status (Valid / Expiring / Expired)
Only after metadata exists → documents are attached.
This prevents:
•	lost documents
•	expired docs hiding in folders
•	audit nightmares
________________________________________
8. HOW LINKING WORKS (SIMPLE RULESET)
Golden Rules
1.	Employee Master never links outward
2.	All other tables link into Employee Master
3.	No circular links
4.	No duplicate identity fields across tables
Standard Linking Pattern
Employee Master
   ↑
   ├── Personal Details
   ├── Compliance
   ├── Bank Details
   ├── Attendance
   ├── Leave
   ├── Requests
   ├── Documents
________________________________________
9. MIGRATION ORDER (DO THIS EXACTLY IN THIS SEQUENCE)
1.	Import Employee Master (core only)
2.	Validate Employee Numbers (duplicates = STOP)
3.	Link Line Managers
4.	Attach Personal Details
5.	Attach Compliance Data
6.	Attach Bank Details
7.	Create empty shells for:
o	Attendance
o	Leave
o	Requests
8.	Only then → documents
________________________________________
10. COMMON MISTAKES TO AVOID (VERY IMPORTANT)
Do not:
•	use names as identifiers
•	merge personal + compliance + employment in one table
•	import documents without metadata
•	allow employees to edit master fields
•	migrate everything “because we already have it”
Migration is controlled exposure, not copying.
________________________________________
11. DELIVERABLE OF THIS STEP
At the end of migration you must have:
•	1 clean Employee Master
•	1 unique identifier per employee
•	0 broken links
•	Partial data allowed
•	Full compliance structure ready

'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.