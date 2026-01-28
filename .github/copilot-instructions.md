# Copilot Coding Agent Instructions

# Repo Principles for Baynunah HR ESS
## Mission
Build a compliant, auditable HR ESS for UAE private sector employers. Prioritize clarity, testability, and UAE labour law alignment.

## Always do this
- Prefer PRs with: (a) spec/plan, (b) implementation, (c) tests, (d) docs, (e) changelog.
- For legal-sensitive changes (attendance, overtime, leave, EOS), **summarize the specific UAE article(s) you relied on and link to official MOHRE/UAE sources** in the PR body.
- Write clean, modular code. Include minimal repro data + scripts for local testing.

## Never do this
- Never rely on non-official blogs for legal statements; prefer MOHRE/UAE law and executive regulations. If unofficial is used for ideas, clearly mark it **non-authoritative**.
- Never commit secrets. Never bypass tests/linters.

## Build & Test
- Node/Yarn workspace (update if different).
- Commands: `npm i && npm run build && npm test`

## Goal & Purpose

This repository contains the **Secure Renewals HR Portal** - a full-stack web application for managing employee contract renewals, onboarding, compliance tracking, and recruitment. Designed for UAE-based startups with solo HR operations, it provides:

- Employee contract renewal management
- Role-based access control (admin, hr, viewer)
- UAE compliance tracking (visa, Emirates ID, medical fitness, ILOE)
- Onboarding workflows with token-based public access
- Recruitment pipeline management
- Audit trails for all actions

**Primary deployment target:** Azure App Service with PostgreSQL database

## Tech Stack

### Infrastructure & Deployment
- **Cloud Platform:** Azure App Service (Linux, Python 3.11 runtime)
- **Database:** Azure PostgreSQL (with SSL, async connections via asyncpg)
- **Infrastructure as Code:** Azure CLI scripts (`deploy_to_azure.sh`) - *no Bicep/Terraform currently*
- **CI/CD:** GitHub Actions
  - `.github/workflows/ci.yml` - Lint checks (Python syntax, npm build)
  - `.github/workflows/deploy.yml` - Automated Azure deployment
  - `.github/workflows/pr-quality-check.yml` - PR validation with security checks
  - `.github/workflows/post-deployment-health.yml` - Post-deploy verification
- **Secrets Management:** GitHub repository secrets + Azure App Service configuration

### Application Stack
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy (async), Alembic, asyncpg, Pydantic
- **Frontend:** React 18, TypeScript, Vite, TailwindCSS
- **Package Management:** `uv` (backend), `npm` (frontend)
- **Database Migrations:** Alembic with async support
- **Auth:** JWT (Employee ID + password)

## Local Run & Test

### Environment Setup

1. **Prerequisites:**
   - Python 3.11+ (with `uv` package manager)
   - Node.js 20+ (required for React Router v7)
   - PostgreSQL (or use SQLite for local dev)

2. **Backend Setup:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your database URL and AUTH_SECRET_KEY
   uv sync                          # Install dependencies
   uv run alembic upgrade head      # Run migrations
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm run dev                      # Starts on port 5173
   ```

4. **VS Code Quick Start:**
   - Press `Ctrl+Shift+B` → "Start Full Application" (runs both backend + frontend)
   - See `.vscode/tasks.json` for all available tasks

### Secrets & Environment Variables

**Backend (`.env` or Azure App Settings):**
- `DATABASE_URL` - PostgreSQL connection string (use `postgresql+asyncpg://` prefix for async)
- `AUTH_SECRET_KEY` - JWT signing key (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `ALLOWED_ORIGINS` - CORS origins (comma-separated)
- Optional: `SMTP_*` settings for email notifications

**Frontend (`.env`):**
- `VITE_API_BASE_URL` - Backend API URL (e.g., `http://localhost:8000/api`)

**Key Vault / GitHub Secrets:**
- Store `DATABASE_URL`, `AUTH_SECRET_KEY`, `AZURE_CREDENTIALS` in GitHub repository secrets
- Azure deployment reads from GitHub secrets and sets as App Service configuration

### Build, Test & Lint Commands

**Backend:**
```bash
cd backend
uv sync                                              # Install deps
uv run python -m py_compile app/**/*.py             # Syntax check
uv run alembic check                                # Verify migrations
uv run alembic revision --autogenerate -m "desc"    # Create migration
```

**Frontend:**
```bash
cd frontend
npm install                                         # Install deps
npm run build                                       # Production build
npm run preview                                     # Preview build
```

**Combined:**
```bash
./scripts/start-portal.sh                           # Start both (macOS/Linux)
scripts\start-portal-windows.bat                    # Start both (Windows)
```

**Note:** No formal test suite currently. Manual testing via:
- Swagger UI: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`

### Sample .env File

See `backend/.env.example` for complete template. Minimal working config:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/hr_portal
AUTH_SECRET_KEY=your-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5000
```

## PR Expectations

### Small, Focused Changes
- Keep PRs small and focused on a single feature/fix
- Split large features into multiple PRs when possible
- Use draft PRs for work-in-progress

### Required Checks
- [ ] Python syntax validation passes (`ci.yml`)
- [ ] No security anti-patterns (string concatenation in SQL, hardcoded secrets, eval/exec)
- [ ] Frontend builds without errors (`npm run build`)
- [ ] Manual testing completed (document in PR description)
- [ ] No accidental commits (check `.gitignore` for build artifacts, `node_modules`, etc.)

### Add/Adjust Tests
- Currently no automated test suite - manual testing required
- Document test evidence in PR (screenshots, API responses, Swagger UI tests)
- For new features: Test via `/docs` (Swagger UI) and document results

### Update Docs & Config When Behavior Changes
- Update `README.md` if setup/deployment steps change
- Update `.github/copilot-instructions.md` if architecture/patterns change
- Update `backend/.env.example` if new environment variables added
- Update `docs/` if user-facing features change
- Update database migrations: `uv run alembic revision --autogenerate -m "description"`

### PR Description Requirements
Use the template in `.github/PULL_REQUEST_TEMPLATE.md`:
- What changed and why
- Testing evidence (screenshots, API responses, manual test steps)
- Deployment impact (migration required? config changes?)
- Security considerations

## Deployment & Branches

### Branch Policy
- **main** - Production branch, protected
  - Requires PR with review
  - CI must pass before merge
  - Triggers automatic Azure deployment via `.github/workflows/deploy.yml`
- **Feature branches** - `feature/description`, `fix/description`, `copilot/description`
  - Created from `main`
  - Merged back to `main` via PR

### Release Flow
1. Create feature branch from `main`
2. Develop & test locally
3. Open PR to `main`
4. CI runs automatically (`ci.yml`, `pr-quality-check.yml`)
5. Review & approval
6. Merge to `main`
7. Automatic deployment to Azure (`deploy.yml`)
8. Post-deployment health check (`post-deployment-health.yml`)

### CI Workflows to Be Aware Of

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Push to main, PRs | Python syntax, npm build |
| `pr-quality-check.yml` | PRs | Security checks, auto-labeling, code quality |
| `deploy.yml` | Push to main, manual | Build frontend, deploy to Azure App Service |
| `post-deployment-health.yml` | After deploy | Health checks, admin account validation |
| `automated-maintenance.yml` | Monthly | Dependency audits, stale branch cleanup |

### Infrastructure Change Review

**Azure deployment script (`deploy_to_azure.sh`):**
- Manual execution required for initial setup
- Creates resource group, App Service plan, web app, PostgreSQL
- Sets required app settings and environment variables

**GitHub Actions deployment (`.github/workflows/deploy.yml`):**
- Automated on push to `main`
- Builds frontend → copies to `backend/static/`
- Deploys to Azure App Service using `AZURE_CREDENTIALS` secret
- Runs database migrations automatically
- Requires secrets: `AZURE_CREDENTIALS`, `DATABASE_URL`, `AUTH_SECRET_KEY`

**Plan/Apply Expectations:**
- No formal infrastructure as code (Bicep/Terraform) - uses Azure CLI scripts
- Infrastructure changes require manual Azure CLI script updates
- Test infrastructure changes in separate resource group first
- Document resource group, plan, and app names in PR

## What to Avoid

### No Secrets in Code or Logs
- ❌ Never commit `.env` files
- ❌ Never hardcode API keys, passwords, connection strings
- ❌ Never log sensitive data (passwords, tokens, personal info)
- ✅ Use environment variables for all secrets
- ✅ Store secrets in GitHub repository secrets
- ✅ Use `sanitize_text()` for user input (prevents XSS)
- ✅ Check `.gitignore` before committing

### No Force Pushes to Protected Branches
- ❌ Never `git push --force` to `main`
- ❌ Never rewrite history on shared branches
- ✅ Use `git revert` for fixing merged commits
- ✅ Create new commits to fix issues

### No Touching Production Infrastructure Without Approval
- ❌ Never manually modify Azure resources in production
- ❌ Never delete production databases or storage
- ❌ Never change production environment variables without coordination
- ✅ Test infrastructure changes in dev/staging first
- ✅ Document all infrastructure changes in PR
- ✅ Get approval before applying infrastructure changes
- ✅ Use Azure CLI scripts for reproducible changes

### Additional Anti-Patterns
- ❌ Don't use string formatting in SQL queries (SQL injection risk)
- ❌ Don't use `eval()` or `exec()` with user input
- ❌ Don't commit `node_modules/`, `__pycache__/`, `.pyc` files
- ❌ Don't mix sync/async database operations
- ❌ Don't expose sensitive routes without authentication

## Definition of Done

A PR is ready to merge when:

- [x] **Lint/Tests Pass**
  - Python syntax validation passes
  - No security anti-patterns detected
  - Frontend builds successfully
  - Manual testing completed and documented

- [x] **CI Green**
  - All GitHub Actions workflows pass
  - No failing checks in PR

- [x] **Docs Updated**
  - README.md reflects any setup/deployment changes
  - `.env.example` includes new environment variables
  - API changes documented in Swagger docstrings
  - User-facing changes documented in `docs/`

- [x] **PR Includes What/Why and Test Evidence**
  - Clear description of changes and rationale
  - Screenshots or API response examples
  - Manual test steps documented
  - Migration instructions if database changes
  - Deployment impact noted (config changes, secrets needed)

- [x] **Security Considerations Addressed**
  - Input sanitization in place (use `sanitize_text()`)
  - No SQL injection vulnerabilities
  - No hardcoded secrets
  - Authentication/authorization properly enforced

- [x] **Ready for Production**
  - Works in both development and production environments
  - No breaking changes without migration path
  - Backward compatible or migration documented
  - Monitoring/logging adequate for troubleshooting

---

## Additional Context

### Architecture Patterns

### Backend: 3-Layer Separation of Concerns
All features follow this pattern (see `backend/app/routers/employees.py` as canonical example):

1. **Router** (`routers/`) - FastAPI endpoints, auth via `require_role(["admin", "hr"])`, request/response handling
2. **Service** (`services/`) - Business logic, validation, orchestration
3. **Repository** (`repositories/`) - Database access using SQLAlchemy async queries

**Critical:** Never put business logic in routers or DB queries in services. Always use the repository layer for data access.

### Database & Migrations

- **Async-only:** All DB ops use `AsyncSession`, not sync Session
- **URL transformation:** Connection strings auto-convert `postgres://` → `postgresql+asyncpg://` (see `backend/app/database.py`)
- **Startup migrations:** `backend/app/startup_migrations.py` runs on app start for data consistency (employee normalization, admin seeding, etc.)
- **Migration commands:**
  ```bash
  cd backend
  uv run alembic upgrade head                  # Apply migrations
  uv run alembic revision --autogenerate -m "" # Generate new migration
  ```

### Frontend: Monolithic State Management

- **Single file:** `frontend/src/App.tsx` (5632 lines) manages all state and API calls
- **API base:** All backend calls use `/api` prefix (e.g., `fetch('/api/employees')`)
- **State:** Global state in `App.tsx`, passed down as props. No Redux/Context.
- **Routing:** Client-side in React; backend serves `index.html` for all non-API paths

## Developer Workflows

### Local Development

```bash
# Backend (port 8000)
cd backend && uv sync && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (port 5173)
cd frontend && npm install && npm run dev

# API docs: http://localhost:8000/docs
```

### VS Code Tasks (Pre-configured)

Use `Ctrl+Shift+B` → "Start Full Application" to run backend + frontend in parallel. See `.vscode/tasks.json`.

### Database Setup

```bash
cd backend
cp .env.example .env  # Edit DATABASE_URL
uv run alembic upgrade head
```

**No test suite:** Use `/docs` (Swagger UI) for manual testing. Production validates via startup migrations.

## Critical Project Conventions

### Authentication Flow

1. **First login:** Employee uses Employee ID + DOB (DDMMYYYY) → forced password change
2. **Subsequent:** Employee ID + new password
3. **JWT:** Stored in `Authorization: Bearer <token>` header; validated via `require_role()` dependency

**Example:** See `backend/app/core/security.py:require_role()` for token validation logic.

### Employee Onboarding (Token-Based Public Flow)

Different from auth! Allows new employees to complete profile before activation:

1. HR/Admin: POST `/api/onboarding/invite` → generates token link
2. Employee: GET `/api/onboarding/validate/{token}` (no auth required)
3. Employee: POST `/api/onboarding/submit` (token in body)
4. HR/Admin: Reviews and approves in admin panel

**Key:** These endpoints have no `require_role()` dependency; token validates access.

### CSV Import Patterns

Employee import (`POST /api/employees/import`) supports **two formats**:

1. **Baynunah format** (auto-detected): Columns like "Employee No", "Employee Name", "Job Title"
2. **Simple format**: Headers `employee_id,name,email,department,date_of_birth,role`

**Critical:** Date parsing handles both `15061990` and `"March 11, 1979"` formats. See `backend/app/services/employees.py:import_from_csv()`.

### UAE Compliance Fields

All employees have compliance tracking fields (see `backend/app/models/employee_compliance.py`):

- Visa (number, issue/expiry dates)
- Emirates ID (number, expiry)
- Medical fitness (date, expiry)
- ILOE (status, expiry)
- Contract (type, start/end dates)

**Feature:** `/api/employees/compliance/alerts?days=60` returns expiring documents.

### Feature Toggles

Admin-only feature flags stored in `system_settings` table:

- GET `/api/admin/features` - List all toggles
- POST `/api/admin/features` - Enable/disable features

**Used for:** Rolling out new modules without code deployment.

## Integration Points

### Static File Serving (Production)

Backend serves frontend build from `backend/static/` or `frontend/dist/` (checks both). See `backend/app/main.py:100-115` for fallback logic.

**SPA routing:** All non-`/api` paths serve `index.html` for client-side routing.

### Deployment Options

- **Local:** `scripts/start-portal.sh` (auto-start available via `scripts/setup-autostart-macos.sh`)
- **Azure:** `deploy_to_azure.sh` + GitHub Actions workflows (see `docs/AZURE_DEPLOYMENT_REFERENCE_GUIDE.md`)
- **Replit:** Pre-configured in `.replit` with custom domain support
- **Codespaces:** Auto-configured dev container for cloud development

### Environment Variables

Required in `backend/.env`:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
AUTH_SECRET_KEY=<random-secret-for-jwt>
ALLOWED_ORIGINS=http://localhost:5173,https://your-domain.com
```

Optional: SMTP settings for email notifications (see `backend/app/core/config.py`).

## Common Implementation Patterns

### Adding a New Feature Module

1. **Model:** Create SQLAlchemy model in `backend/app/models/your_feature.py`
2. **Schema:** Pydantic models in `backend/app/schemas/your_feature.py` with validators
3. **Repository:** DB queries in `backend/app/repositories/your_feature.py`
4. **Service:** Business logic in `backend/app/services/your_feature.py`
5. **Router:** API endpoints in `backend/app/routers/your_feature.py` with `require_role()`
6. **Register:** Import in `backend/app/main.py` and `app.include_router(your_feature.router)`
7. **Migration:** Generate with `uv run alembic revision --autogenerate`
8. **Frontend:** Add component in `frontend/src/components/YourFeature.tsx`, integrate in `App.tsx`

**Example:** See `backend/app/routers/passes.py` for complete pattern (43-line router with 5 endpoints).

### Pydantic Validation + Sanitization

Always use `sanitize_text()` for user input (HTML escape):

```python
from app.core.security import sanitize_text
from pydantic import field_validator

@field_validator("name")
@classmethod
def sanitize_name(cls, value: str) -> str:
    return sanitize_text(value)
```

### Async Repository Pattern

```python
# Repository
async def list_all(self, session: AsyncSession) -> Sequence[Employee]:
    result = await session.execute(select(Employee).order_by(Employee.name))
    return result.scalars().all()

# Service
async def list_employees(self, session: AsyncSession) -> List[EmployeeResponse]:
    repo = EmployeeRepository()
    employees = await repo.list_all(session)
    return [EmployeeResponse.model_validate(e) for e in employees]
```

## AI Agent Ecosystem

This project has specialized agents for different tasks:

- **HR Assistant** (`.github/agents/hr-assistant.md`) - HR workflows, planning, module discovery
- **Portal Engineer** (`.github/agents/portal-engineer.md`) - Full-stack implementation, debugging
- **Code Quality Monitor** (`.github/agents/code-quality-monitor.md`) - Security scans, performance checks
- **Azure Debugger** (`.github/agents/azure-debugger.md`) - Break/fix for Azure deployments and pipelines
- **Azure Deployment Engineer** (`.github/agents/azure-deployment-engineer.md`) - End-to-end Azure deployment setup and automation

**Usage:** Reference agent files for specialized tasks. Example: "Use Portal Engineer pattern to add probation tracking."

## Key Files Reference

- `backend/app/main.py` - App factory, router registration, static serving, startup migrations
- `backend/app/core/security.py` - JWT validation, role checking, input sanitization
- `backend/app/database.py` - Async SQLAlchemy setup, session factory
- `backend/app/startup_migrations.py` - Data consistency fixes on app start
- `frontend/src/App.tsx` - All frontend state, components, API calls (5632 lines)
- `docs/COPILOT_AGENTS.md` - Complete agent documentation
- `docs/AZURE_DEPLOYMENT_REFERENCE_GUIDE.md` - Cloud deployment patterns

---

## Security Patterns

### Input Sanitization (Required for All User Input)

Always use `sanitize_text()` for any user-provided text to prevent XSS attacks:

```python
from app.core.security import sanitize_text
from pydantic import field_validator

class EmployeeCreate(BaseModel):
    name: str
    department: Optional[str] = None
    
    @field_validator("name")
    @classmethod
    def sanitize_name(cls, value: str) -> str:
        return sanitize_text(value)  # HTML escapes dangerous characters
    
    @field_validator("department")
    @classmethod
    def sanitize_department(cls, value: Optional[str]) -> Optional[str]:
        return sanitize_text(value) if value else None
```

### SQL Injection Prevention

**Always use parameterized queries.** Never use string interpolation for SQL:

```python
# ❌ NEVER do this - SQL injection vulnerability
async def get_employee_bad(self, db: AsyncSession, employee_id: str):
    result = await db.execute(text(f"SELECT * FROM employees WHERE employee_id = '{employee_id}'"))
    return result.scalar_one_or_none()

# ✅ ALWAYS do this - parameterized query
async def get_employee_safe(self, db: AsyncSession, employee_id: str):
    result = await db.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    return result.scalar_one_or_none()

# ✅ If using raw SQL, use named parameters
async def get_employee_raw_safe(self, db: AsyncSession, employee_id: str):
    result = await db.execute(
        text("SELECT * FROM employees WHERE employee_id = :emp_id"),
        {"emp_id": employee_id}
    )
    return result.fetchone()
```

### JWT Authentication Flow

The authentication system uses Employee ID + password with JWT tokens:

```python
# 1. Login generates JWT token
# See: backend/app/routers/auth.py
@router.post("/login")
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session)):
    return await employee_service.login(session, request)

# 2. Protected endpoints use require_role() dependency
# See: backend/app/core/security.py
@router.get("/employees")
async def list_employees(
    role: str = Depends(require_role(["admin", "hr"])),
    session: AsyncSession = Depends(get_session)
):
    # role is validated before this code runs
    return await employee_service.list_employees(session)

# 3. JWT payload structure
payload = {
    "sub": employee.employee_id,  # Subject (employee ID)
    "name": employee.name,
    "role": employee.role,        # "admin", "hr", or "viewer"
    "exp": expire,                # Expiration datetime
    "iat": datetime.now(timezone.utc),
}
```

---

## Troubleshooting Guide

### Common Login Issues

**Error: "An error occurred during login"**

This generic error appears when an unexpected exception occurs. Check:

1. **Database connection**: Verify DATABASE_URL is correct
   ```bash
   # Check health endpoint
   curl https://your-app.azurewebsites.net/api/health/db
   ```

2. **Admin password reset**: If admin password is corrupted
   ```bash
   curl -X POST https://your-app.azurewebsites.net/api/health/reset-admin-password \
     -H "X-Admin-Secret: YOUR_AUTH_SECRET_KEY"
   ```

3. **SSL connection**: Azure PostgreSQL requires SSL
   - Ensure DATABASE_URL includes `sslmode=require`
   - The `db_utils.py` handles SSL parameter extraction automatically

### Async/Sync Mismatch Errors

**Error: "async_generator object has no attribute 'execute'"**

This happens when mixing async/sync code incorrectly:

```python
# ❌ WRONG - Missing await
def get_employee_sync(self, db: AsyncSession, employee_id: str):
    result = db.execute(select(Employee))  # Missing await!
    return result.scalar_one_or_none()

# ✅ CORRECT - All async operations awaited
async def get_employee_async(self, db: AsyncSession, employee_id: str):
    result = await db.execute(select(Employee))
    return result.scalar_one_or_none()
```

**Error: "cannot schedule new futures after shutdown"**

This occurs when the event loop closes before async tasks complete:

```python
# ❌ WRONG - Event loop closes before task completes
async def bad_pattern():
    asyncio.create_task(some_long_task())  # Fire and forget - may not complete
    return {"status": "ok"}

# ✅ CORRECT - Await the task or use background tasks properly
async def good_pattern():
    await some_long_task()  # Wait for completion
    return {"status": "ok"}

# ✅ For background tasks, use FastAPI's BackgroundTasks
@router.post("/send-email")
async def send_email(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email_async)
    return {"status": "queued"}
```

### Database Connection Issues

**Error: "connection refused" or "timeout"**

1. Check DATABASE_URL format:
   ```
   postgresql+asyncpg://user:password@host:5432/dbname?sslmode=require
   ```

2. For Azure PostgreSQL, ensure:
   - Firewall rules allow your IP/Azure services
   - SSL is enabled (handled automatically by `db_utils.py`)
   - Connection string uses `postgresql+asyncpg://` prefix

**Error: "column does not exist"**

Run migrations:
```bash
cd backend
uv run alembic upgrade head
```

If migrations fail, check `alembic/versions/` for conflicting migrations.

### Migration Conflicts

When multiple developers create migrations simultaneously:

```bash
# 1. Check current migration state
uv run alembic current

# 2. If you see multiple heads, merge them
uv run alembic merge heads -m "merge_migrations"

# 3. Apply the merged migration
uv run alembic upgrade head
```

---

## Complete Feature Implementation Example

### Employee Notes Module

This example shows how to implement a complete feature following the 3-layer architecture.

#### 1. Model (backend/app/models/employee_note.py)

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.renewal import Base

class EmployeeNote(Base):
    __tablename__ = "employee_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(20), ForeignKey("employees.employee_id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    note_type = Column(String(50), default="general")  # general, performance, disciplinary
    created_by = Column(String(20), nullable=False)  # Employee ID of author
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to employee
    employee = relationship("Employee", back_populates="notes")
```

#### 2. Schema (backend/app/schemas/employee_note.py)

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from app.core.security import sanitize_text

class EmployeeNoteBase(BaseModel):
    content: str
    note_type: str = "general"
    
    @field_validator("content")
    @classmethod
    def sanitize_content(cls, value: str) -> str:
        return sanitize_text(value)
    
    @field_validator("note_type")
    @classmethod
    def validate_note_type(cls, value: str) -> str:
        allowed = {"general", "performance", "disciplinary"}
        if value not in allowed:
            raise ValueError(f"note_type must be one of: {allowed}")
        return value

class EmployeeNoteCreate(EmployeeNoteBase):
    employee_id: str

class EmployeeNoteResponse(EmployeeNoteBase):
    id: int
    employee_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### 3. Repository (backend/app/repositories/employee_notes.py)

```python
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.employee_note import EmployeeNote

class EmployeeNoteRepository:
    async def create(
        self, db: AsyncSession, employee_id: str, content: str, 
        note_type: str, created_by: str
    ) -> EmployeeNote:
        note = EmployeeNote(
            employee_id=employee_id,
            content=content,
            note_type=note_type,
            created_by=created_by
        )
        db.add(note)
        await db.flush()
        await db.refresh(note)
        return note
    
    async def list_by_employee(
        self, db: AsyncSession, employee_id: str
    ) -> Sequence[EmployeeNote]:
        result = await db.execute(
            select(EmployeeNote)
            .where(EmployeeNote.employee_id == employee_id)
            .order_by(EmployeeNote.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_id(self, db: AsyncSession, note_id: int) -> EmployeeNote | None:
        result = await db.execute(
            select(EmployeeNote).where(EmployeeNote.id == note_id)
        )
        return result.scalar_one_or_none()
    
    async def delete(self, db: AsyncSession, note_id: int) -> bool:
        note = await self.get_by_id(db, note_id)
        if note:
            await db.delete(note)
            return True
        return False
```

#### 4. Service (backend/app/services/employee_notes.py)

```python
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.employee_notes import EmployeeNoteRepository
from app.schemas.employee_note import EmployeeNoteCreate, EmployeeNoteResponse

class EmployeeNoteService:
    def __init__(self):
        self._repo = EmployeeNoteRepository()
    
    async def create_note(
        self, db: AsyncSession, data: EmployeeNoteCreate, created_by: str
    ) -> EmployeeNoteResponse:
        note = await self._repo.create(
            db, data.employee_id, data.content, data.note_type, created_by
        )
        await db.commit()
        return EmployeeNoteResponse.model_validate(note)
    
    async def get_employee_notes(
        self, db: AsyncSession, employee_id: str
    ) -> List[EmployeeNoteResponse]:
        notes = await self._repo.list_by_employee(db, employee_id)
        return [EmployeeNoteResponse.model_validate(n) for n in notes]
    
    async def delete_note(
        self, db: AsyncSession, note_id: int, user_role: str
    ) -> bool:
        if user_role not in ["admin", "hr"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin/HR can delete notes"
            )
        deleted = await self._repo.delete(db, note_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        await db.commit()
        return True

employee_note_service = EmployeeNoteService()
```

#### 5. Router (backend/app/routers/employee_notes.py)

```python
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import require_role
from app.database import get_session
from app.schemas.employee_note import EmployeeNoteCreate, EmployeeNoteResponse
from app.services.employee_notes import employee_note_service

router = APIRouter(prefix="/employee-notes", tags=["employee-notes"])

@router.post("", response_model=EmployeeNoteResponse)
async def create_note(
    data: EmployeeNoteCreate,
    role: str = Depends(require_role(["admin", "hr"])),
    db: AsyncSession = Depends(get_session),
):
    """Create a new note for an employee. Requires admin or HR role."""
    # Use employee_id from the token in a real implementation
    return await employee_note_service.create_note(db, data, created_by="SYSTEM")

@router.get("/{employee_id}", response_model=List[EmployeeNoteResponse])
async def get_notes(
    employee_id: str,
    role: str = Depends(require_role(["admin", "hr"])),
    db: AsyncSession = Depends(get_session),
):
    """Get all notes for an employee. Requires admin or HR role."""
    return await employee_note_service.get_employee_notes(db, employee_id)

@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    role: str = Depends(require_role(["admin", "hr"])),
    db: AsyncSession = Depends(get_session),
):
    """Delete a note. Requires admin or HR role."""
    await employee_note_service.delete_note(db, note_id, role)
    return {"success": True, "message": "Note deleted"}
```

#### 6. Register Router (backend/app/main.py)

```python
from app.routers import employee_notes

# Add to router registration section
app.include_router(employee_notes.router, prefix="/api")
```

#### 7. Generate Migration

```bash
cd backend
uv run alembic revision --autogenerate -m "add_employee_notes_table"
uv run alembic upgrade head
```

#### 8. Frontend Integration (frontend/src/App.tsx)

```typescript
// Add to API calls section
const fetchEmployeeNotes = async (employeeId: string) => {
  const response = await fetch(`/api/employee-notes/${employeeId}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.json();
};

const createEmployeeNote = async (data: { employee_id: string; content: string; note_type: string }) => {
  const response = await fetch('/api/employee-notes', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });
  return response.json();
};
```

---

## Development Tools Reference

### VS Code Tasks (.vscode/tasks.json)

- **Start Full Application**: `Ctrl+Shift+B` - Runs both frontend and backend
- **Start Backend Only**: Runs FastAPI server on port 8000
- **Start Frontend Only**: Runs Vite dev server on port 5173
- **Run Migrations**: Executes `alembic upgrade head`

### VS Code Debug Configurations (.vscode/launch.json)

- **Python: FastAPI**: Debug backend with breakpoints
- **Chrome: Frontend**: Debug React app in Chrome
- **Full Stack**: Debug both simultaneously

### GitHub Workflows (.github/workflows/)

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| `ci.yml` | Run tests and linting | Push to main, PRs |
| `deploy.yml` | Deploy to Azure | Push to main (after CI) |
| `pr-quality-check.yml` | PR validation | Pull requests |
| `post-deployment-health.yml` | Verify deployment | After deploy |

### Useful Commands

```bash
# Backend
cd backend
uv sync                                    # Install dependencies
uv run uvicorn app.main:app --reload      # Start dev server
uv run alembic upgrade head                # Apply migrations
uv run alembic revision --autogenerate -m "description"  # Create migration

# Frontend
cd frontend
npm install                                # Install dependencies
npm run dev                                # Start dev server
npm run build                              # Production build

# Combined
./scripts/start-portal.sh                  # Start both (macOS/Linux)
scripts\start-portal-windows.bat          # Start both (Windows)
```

---

**For full documentation:** See [README.md](../README.md) | [CONTRIBUTING.md](../CONTRIBUTING.md) | [docs/](../docs/)
