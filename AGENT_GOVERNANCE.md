# AGENT GOVERNANCE

## Purpose
Define boundaries, permissions, and escalation for all agents in this repository.

## Agents and scopes
- **HR Assistant:** HR workflows, compliance guidance, feature planning. *Read/advise only; no direct infra changes.*
- **Portal Engineer:** Full-stack implementation guidance. *Code changes allowed within PR scope; no production infra changes.*
- **Code Quality Monitor:** Security/perf/quality scans. *Read/advise; may propose patches.*
- **Azure Deployment Specialist / Azure Debugger:** Deployment and Azure troubleshooting. *May modify workflows/config under PR; no secret handling.*
- **Technical Guardian / Aesthetic Guardian:** UI/UX and quality guardrails. *Advisory.*
- **Repo Steward (one-off):** Autonomous remediation per `repo-steward.md`; must stop after Phase 6.
- **OSS Scout / Guardian HR UAE / My Agent:** Advisory or scoped to compliance/OSS research; no unbounded write.

## Permissions model
- **Read-only:** Advisory agents (HR Assistant, Code Quality Monitor, Aesthetic/Technical Guardian) unless explicitly invoked for code edits.
- **Write (within PR scope):** Portal Engineer, Azure Deployment Specialist/Debugger, Repo Steward during active mandate.
- **No secrets:** Agents must never create, expose, or store credentials/tokens. Use environment/config only.

## Escalation rules
- Security or compliance concerns → flag in PR and halt risky changes.
- Infra deployment changes → require explicit approval and align with `deploy.yml` path.
- HR law-sensitive areas (working hours, overtime, leave, WPS) → cite UAE Federal Decree-Law 33/2021 & Cabinet Resolution 1/2022 with article references in PR.

## Usage rules
- Prefer single canonical entry point: see `START_HERE.md`.
- Agents must reference this governance file when giving instructions.
- Autonomous agents (e.g., Repo Steward) must self-terminate after completing their defined phases.
