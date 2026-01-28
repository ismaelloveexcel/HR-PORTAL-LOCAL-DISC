# Agent Inventory & Deployment Status

> **Generated:** 2026-01-25  
> **Updated:** 2026-01-25 (Deployed 3 new agents)  
> **Purpose:** Comprehensive list of all agents in the HR Portal repository with their purpose and deployment status.

---

## Summary

| Total Agents | Deployed as Bots | Instructions Only | Advisory/Research |
|--------------|------------------|-------------------|-------------------|
| **12**       | **5**            | **5**             | **2**             |

---

## Agent Categories

### 🤖 **DEPLOYED AS AUTOMATED BOTS** (5)

These agents have GitHub Actions workflows that run automatically.

| # | Agent | File | Workflow | Trigger | Status |
|---|-------|------|----------|---------|--------|
| 1 | **Technical Guardian** | `.github/agents/technical-guardian.md` | `technical-guardian-health.yml`<br>`technical-guardian-security.yml` | Every 15 min (health)<br>Daily + PRs (security) | ✅ **ACTIVE** |
| 2 | **Aesthetic Guardian** | `.github/agents/aesthetic-guardian.md` | `aesthetic-guardian-pr.yml` | On PRs (frontend files) | ✅ **ACTIVE** |
| 3 | **Azure Debugger** | `.github/agents/azure-debugger.md` | `azure-debugger-monitor.yml` | On deployment failures + manual | ✅ **ACTIVE** |
| 4 | **Code Quality Monitor** | `.github/agents/code-quality-monitor.md` | `code-quality-monitor.yml` | PRs + push to main + weekly | ✅ **ACTIVE** |
| 5 | **Azure Deployment Engineer** | `.github/agents/azure-deployment-engineer.md` | `azure-deployment-engineer.yml` | On infra changes + PRs | ✅ **ACTIVE** |

---

### 📋 **INSTRUCTION-BASED AGENTS** (5)

These agents exist as instruction files for GitHub Copilot Chat or manual reference. They are **not deployed as automated bots** but can be invoked manually with Copilot.

| # | Agent | File | Purpose | Deployment Status |
|---|-------|------|---------|-------------------|
| 1 | **HR Assistant** | `.github/agents/hr-assistant.md` | HR workflows, compliance guidance, feature planning, employee management | 📋 Instructions Only |
| 2 | **Portal Engineer** | `.github/agents/portal-engineer.md` | Full-stack implementation, API development, database design, bug fixes | 📋 Instructions Only |
| 3 | **Azure Deployment Specialist** | `.github/agents/azure-deployment-specialist.md` | Azure deployment through VS Code, troubleshooting, login issues | 📋 Instructions Only |
| 4 | **Repo Steward** | `.github/agents/repo-steward.md` | One-off autonomous repository stabilisation and governance (self-terminating) | 📋 Instructions Only (One-off) |
| 5 | **My Agent** | `.github/agents/my-agent.agent.md` | Custom deployment guardrails for OIDC pattern | 📋 Instructions Only |

---

### 🔬 **COPILOT AGENTS (with agent metadata)** (2)

These agents use the GitHub Copilot agent format (`.agent.md`) and are designed for automatic invocation.

| # | Agent | File | Purpose | Deployment Status |
|---|-------|------|---------|-------------------|
| 1 | **Guardian HR-UAE** | `.github/agents/guardian-hr-uae.agent.md` | Autonomous HR engineering, process architecture, UAE labour law compliance | 🎯 Copilot Agent (Active) |
| 2 | **OSS Scout** | `.github/agents/oss-scout.agent.md` | Research-first agent for finding/evaluating open-source modules | 🎯 Copilot Agent (Active) |

---

## Detailed Agent Descriptions

### 1. Technical Guardian ✅ DEPLOYED

**File:** `.github/agents/technical-guardian.md`

**Purpose:** System health monitoring, proactive issue detection, security scanning, and automated fixes.

**Automated Features:**
- ✅ **Health monitoring** every 15 minutes via `technical-guardian-health.yml`
  - Checks `/api/health/ping` and `/api/health/db`
  - Creates GitHub issues automatically if health checks fail
- ✅ **Security scanning** daily + on PRs via `technical-guardian-security.yml`
  - Trivy vulnerability scanning
  - Python security checks (Safety, Bandit)
  - NPM audit for frontend
  - Secret detection in code
  - Posts results to PRs and creates issues for critical findings

**Capabilities:**
- Database performance monitoring
- API response time analysis
- Memory/CPU usage monitoring
- Code quality analysis
- N+1 query detection
- Missing index identification

---

### 2. Aesthetic Guardian ✅ DEPLOYED

**File:** `.github/agents/aesthetic-guardian.md`

**Purpose:** UI/UX quality assurance, visual consistency, accessibility compliance.

**Automated Features:**
- ✅ **UI/UX review** on every PR modifying frontend files via `aesthetic-guardian-pr.yml`
  - Color contrast analysis
  - Responsive design checks (sm:, md:, lg:, xl: classes)
  - Loading states verification
  - Button states review (hover/focus/disabled)
  - Typography consistency analysis
  - Posts detailed review as PR comment

**Design Standards Enforced:**
- WCAG 2.1 AA compliance
- TailwindCSS utility class consistency
- Responsive breakpoint coverage
- Interactive element states

---

### 3. Azure Debugger ✅ DEPLOYED

**File:** `.github/agents/azure-debugger.md`

**Purpose:** Automated diagnosis and resolution of Azure deployment failures.

**Automated Features:**
- ✅ **Deployment failure monitoring** via `azure-debugger-monitor.yml`
  - Triggered automatically when Deploy/CI workflows fail
  - Can be manually triggered for analysis
- ✅ **Automated failure analysis**
  - Gets failed job details and logs
  - Identifies common error patterns (OIDC, CORS, DB connection, etc.)
  - Validates infrastructure files
- ✅ **Diagnostic issue creation**
  - Creates GitHub issues with detailed analysis
  - Includes recommended actions and quick fix commands

**Key Capabilities:**
- Automated failure analysis
- Bicep template validation
- GitHub Actions workflow debugging
- Backend startup issue detection
- Database connection diagnosis
- CORS configuration checks
- OIDC authentication verification

---

### 4. Code Quality Monitor ✅ DEPLOYED

**File:** `.github/agents/code-quality-monitor.md`

**Purpose:** Proactive code quality and security scanner.

**Automated Features:**
- ✅ **Code quality analysis** via `code-quality-monitor.yml`
  - Triggered on PRs and push to main
  - Weekly scheduled comprehensive scan
- ✅ **Python quality checks**
  - Flake8 linting
  - mypy type checking
  - Radon complexity analysis
  - Vulture dead code detection
- ✅ **Frontend quality checks**
  - TypeScript compilation
  - 'any' type usage detection
  - React best practices validation
- ✅ **PR comments and weekly reports**
  - Detailed quality report on PRs
  - Weekly summary issues

**Detection Patterns:**
- Critical linting issues
- Type safety violations
- High complexity functions
- Dead code
- Console.log statements
- Missing key props in React

---

### 5. Azure Deployment Engineer ✅ DEPLOYED

**File:** `.github/agents/azure-deployment-engineer.md`

**Purpose:** End-to-end Azure deployment validation and setup.

**Automated Features:**
- ✅ **Infrastructure validation** via `azure-deployment-engineer.yml`
  - Triggered on changes to infra/, workflows, or dependency files
  - Validates Bicep templates
  - Checks workflow YAML syntax
- ✅ **Deployment configuration check**
  - Verifies required files exist
  - Checks environment variable documentation
  - Analyzes secrets usage in workflows
- ✅ **Readiness assessment**
  - Calculates deployment readiness score
  - Creates issues if configuration is incomplete

**Key Capabilities:**
- Bicep template validation
- Workflow file analysis
- Required files verification
- Environment variables check
- Deployment readiness scoring

---

### 6. HR Assistant 📋 NOT DEPLOYED

**File:** `.github/agents/hr-assistant.md`

**Purpose:** Expert HR Assistant and Portal System Engineer for solo HR professionals.

**Key Capabilities:**
- Employee management guidance
- Contract renewals workflow assistance
- Compliance and audit support
- Bulk employee imports
- Onboarding workflow design
- Probation tracking setup

**Use When:**
- Planning HR features
- Importing employee data
- Setting up compliance reports
- Understanding HR module features

**To Deploy:** Would require building GitHub Actions workflows that implement the agent's logic for automated HR workflow assistance.

---

### 7. Portal Engineer 📋 NOT DEPLOYED

**File:** `.github/agents/portal-engineer.md`

**Purpose:** Full-stack development specialist for technical implementation.

**Key Capabilities:**
- Feature implementation (backend + frontend)
- API development with FastAPI
- Database design and migrations
- React component development
- Performance optimization
- Bug fixing

**Code Patterns Defined:**
- Router pattern (FastAPI)
- Service layer pattern
- Repository pattern
- Pydantic schemas
- TypeScript React components

**To Deploy:** Would require integration with code generation tools or PR automation for implementation assistance.

---

### 8. Azure Deployment Specialist 📋 NOT DEPLOYED

**File:** `.github/agents/azure-deployment-specialist.md`

**Purpose:** Expert in Azure deployment, VS Code integration, and troubleshooting.

**Key Capabilities:**
- VS Code deployment guidance
- GitHub Actions deployment setup
- Login/authentication troubleshooting
- Database connection debugging
- Python environment fixes
- Emergency recovery procedures

**Contains:**
- Complete deployment commands
- Troubleshooting guides for common issues
- Emergency recovery procedures
- Health endpoint documentation

**To Deploy:** Could be integrated into deployment workflows for automated troubleshooting or ChatOps.

---

### 9. Repo Steward 📋 NOT DEPLOYED (One-Off)

**File:** `.github/agents/repo-steward.md`

**Purpose:** One-time autonomous repository stabilization and governance.

**Execution Phases:**
1. Repository scan (read-only)
2. Create `START_HERE.md` entry point
3. Documentation consolidation
4. Architecture clarification
5. Agent governance setup
6. Repository hygiene
7. Final report and self-retirement

**Self-Termination:** Agent must stop after Phase 6 completion.

**Deployment Status:** Designed for one-off execution, not continuous operation. Already completed its mandate (based on existing `START_HERE.md`, `ARCHITECTURE_OVERVIEW.md`, and `AGENT_GOVERNANCE.md`).

---

### 10. My Agent 📋 NOT DEPLOYED

**File:** `.github/agents/my-agent.agent.md`

**Purpose:** Custom deployment guardrails for "my agent" aligned to Azure OIDC pattern.

**Rules:**
1. OIDC permissions required (`id-token: write`, `contents: read`)
2. No client secret with `azure/login@v2`
3. Mandatory GitHub secrets validation
4. Workflow verification

**To Deploy:** Acts as a governance guide; no separate automation needed.

---

### 11. Guardian HR-UAE 🎯 COPILOT AGENT

**File:** `.github/agents/guardian-hr-uae.agent.md`

**Purpose:** Autonomous HR Engineering, Process, Design & Compliance Partner for UAE private-sector HR ESS platform.

**Unique Features:**
- **UAE Labour Law Compliance** - Cites Federal Decree-Law 33/2021, Cabinet Resolution 1/2022
- **HR Bottleneck Framework** - Diagnoses issues by Volume, Approval, Data, Tooling, Policy ambiguity
- **Quality Gate Self-Scoring** - Must score ≥4 on simplicity, process clarity, HR control, audit defensibility
- **Visual Constraints** - Strict design system (white-dominant, green icons only, no gradients)
- **Kill Switch** - Must stop and escalate when ambiguity or compliance risk detected

**Operating Modes:**
- Advisor Mode (default) - Diagnose and recommend
- Builder Mode - Activated on explicit instruction

**Decision Authority:**
- Auto-approve: UX flows, additive data model, technical implementation
- Require approval: Breaking data model, HR policy interpretation

**Deployment Status:** Active as GitHub Copilot agent (auto-selected when tasks match).

---

### 12. OSS Scout 🎯 COPILOT AGENT

**File:** `.github/agents/oss-scout.agent.md`

**Purpose:** Research-first Copilot agent for finding and evaluating open-source modules.

**Core Behaviors:**
- **Research-first** - Searches GitHub for suitable modules/patterns
- **Evidence-based** - Provides ranked shortlists with metrics (stars, last update, license)
- **Decide & Deliver** - Recommends best option or justifies building from scratch
- **Compliance-aware** - Includes UAE Compliance Summary when applicable

**Deliverables:**
1. Shortlist (3-5 GitHub candidates) with adaptation effort estimates
2. Recommendation with trade-offs
3. PR with implementation, tests, docs, and provenance

**Evaluation Heuristics:**
- Active maintenance
- Permissive licenses (MIT/Apache-2.0/BSD)
- Good documentation
- Test coverage
- Compatible stack

**Deployment Status:** Active as GitHub Copilot agent (auto-selected when tasks match).

---

## Agents Yet to Be Deployed

The following agents remain as **instruction-only** (not deployed as automated bots):

| Agent | Potential Deployment | Effort | Priority |
|-------|---------------------|--------|----------|
| HR Assistant | Automated HR workflow notifications | Medium | Low |
| Portal Engineer | Code generation assistance | High | Low |
| Azure Deployment Specialist | ChatOps deployment commands | Medium | Medium |

**Recently Deployed (2026-01-25):**
- ✅ **Azure Debugger** - Now monitors deployment failures automatically
- ✅ **Code Quality Monitor** - Now runs on PRs and weekly
- ✅ **Azure Deployment Engineer** - Now validates infrastructure on changes

---

## Agent Collaboration Model

Based on `config.yml`, agents work together in phases:

```
Planning Phase:
  Primary: Guardian HR-UAE
  Secondary: HR Assistant, Portal Engineer, OSS Scout

Research Phase:
  Primary: OSS Scout
  Secondary: Guardian HR-UAE

Implementation Phase:
  Primary: Portal Engineer
  Secondary: Code Quality Monitor, Guardian HR-UAE

Quality Assurance Phase:
  Primary: Code Quality Monitor
  Secondary: Portal Engineer, Guardian HR-UAE

Deployment Phase:
  Primary: Azure Deployment Specialist
  Secondary: Portal Engineer, Code Quality Monitor

Production Maintenance:
  Primary: Code Quality Monitor
  Secondary: HR Assistant, Portal Engineer, Azure Deployment Specialist, Guardian HR-UAE

Compliance Review:
  Primary: Guardian HR-UAE
  Secondary: HR Assistant, Code Quality Monitor
```

---

## Governance Reference

All agents must follow rules defined in:
- `AGENT_GOVERNANCE.md` - Boundaries, permissions, escalation rules
- `.github/agents/config.yml` - Agent configuration and collaboration

**Key Governance Rules:**
- Read-only: Advisory agents unless explicitly invoked for code edits
- Write (within PR scope): Portal Engineer, Azure Deployment Specialist/Debugger
- No secrets: Agents must never create, expose, or store credentials
- Escalation: Security/compliance concerns must be flagged and risky changes halted

---

## How to Use Agents

### Using Deployed Bots
The following agents run automatically and post results in GitHub:

| Agent | Output Location |
|-------|-----------------|
| Technical Guardian | Issues (health alerts), PRs (security scans) |
| Aesthetic Guardian | PRs (UI/UX reviews) |
| Azure Debugger | Issues (deployment failure analysis) |
| Code Quality Monitor | PRs (quality reports), Issues (weekly reports) |
| Azure Deployment Engineer | PRs (infrastructure validation), Issues (if config incomplete) |

### Using Instruction Agents with Copilot
In VS Code or GitHub Copilot Chat:
```
"Using the [Agent Name] agent instructions, [your request]"

Examples:
"Using the Portal Engineer agent instructions, add a leave management module"
"Using the Azure Debugger agent instructions, fix the deployment failure"
"Using the HR Assistant agent instructions, help me import employees from CSV"
```

### Using Copilot Agents
Guardian HR-UAE and OSS Scout are auto-selected by Copilot when tasks match their triggers. You can also explicitly invoke them:
```
"@guardian-hr-uae design a UAE-compliant overtime tracking feature"
"@oss-scout find an open-source leave management module"
```

---

## Related Documentation

- [Agent Integration Guide](../AGENT_INTEGRATION_GUIDE.md)
- [Agent Governance](../AGENT_GOVERNANCE.md)
- [Agents README](../.github/agents/README.md)
- [Quick Reference](../.github/agents/QUICK_REFERENCE.md)

---

*Last Updated: 2026-01-25 (Deployed Azure Debugger, Code Quality Monitor, Azure Deployment Engineer)*
