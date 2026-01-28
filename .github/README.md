# .github Directory Guide

> 📂 **Navigation guide for the GitHub configuration directory**

This directory contains all GitHub-specific configurations including workflows, templates, and Copilot instructions.

---

## 📋 Directory Structure

```
.github/
├── README.md                    # This file - navigation guide
├── copilot-instructions.md      # Coding guidelines for GitHub Copilot
├── COPILOT_SETUP_SUMMARY.md     # Enhancement summary and validation checklist
├── PULL_REQUEST_TEMPLATE.md     # PR template with checklist
├── dependabot.yml               # Dependency update configuration
├── labeler.yml                  # Auto-labeling rules for PRs
│
├── agents/                      # Specialized Copilot agents
│   ├── hr-assistant.md          # HR workflows & planning
│   ├── portal-engineer.md       # Technical implementation
│   ├── code-quality-monitor.md  # Security & quality scanning
│   └── azure-deployment-specialist.md  # Azure deployment
│
├── chatmodes/                   # Copilot chat mode configurations
│
├── instructions/                # Additional instruction sets
│
├── ISSUE_TEMPLATE/              # Issue templates
│   ├── bug_report.md
│   └── feature_request.md
│
└── workflows/                   # GitHub Actions workflows
    ├── ci.yml                   # Continuous integration
    ├── deploy.yml               # Deployment to Azure
    ├── pr-quality-check.yml     # PR validation
    └── ...
```

---

## 🤖 Copilot Configuration

### copilot-instructions.md

The main coding guidelines file (580+ lines) containing:

| Section | Description |
|---------|-------------|
| **Project Overview** | Tech stack, architecture patterns |
| **Security Patterns** | Input sanitization, SQL injection prevention, JWT auth |
| **Troubleshooting** | Common errors and solutions |
| **Feature Example** | Complete Employee Notes implementation |
| **Development Tools** | VS Code tasks, debug configs, commands |

### Security Pattern Example

```python
from app.core.security import sanitize_text
from pydantic import field_validator

class EmployeeCreate(BaseModel):
    name: str
    
    @field_validator("name")
    @classmethod
    def sanitize_name(cls, value: str) -> str:
        return sanitize_text(value)  # HTML escapes dangerous characters
```

---

## 🔄 Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Push, PRs | Run tests and linting |
| `deploy.yml` | Push to main | Deploy to Azure App Service |
| `pr-quality-check.yml` | Pull requests | Validate code quality |
| `post-deployment-health.yml` | After deployment | Verify deployment health |
| `automated-maintenance.yml` | Monthly schedule | Dependency audits, cleanup |
| `addon-discovery.yml` | Monthly schedule | Find integration opportunities |
| `security-monitoring.yml` | Schedule | Security vulnerability checks |

---

## 📝 Templates

### Pull Request Template

The `PULL_REQUEST_TEMPLATE.md` includes:
- Change type checkboxes
- Testing checklist
- Security review checklist
- Documentation checklist

### Issue Templates

Located in `ISSUE_TEMPLATE/`:
- **Bug Report**: For reporting bugs with reproduction steps
- **Feature Request**: For new feature proposals

---

## 🤖 Specialized Agents

Located in `agents/`:

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| **HR Assistant** | HR workflows, planning | Feature planning, automation ideas |
| **Portal Engineer** | Technical implementation | Building features, fixing bugs |
| **Code Quality Monitor** | Security & quality | Code reviews, vulnerability checks |
| **Azure Deployment Specialist** | Azure deployment | Deploy issues, configuration |

### Usage

```bash
# In GitHub Copilot Chat, reference an agent:
@workspace Use the Portal Engineer pattern to add probation tracking
```

---

## ⚙️ Configuration Files

### dependabot.yml

Configures automatic dependency updates:
- Python packages (weekly)
- npm packages (weekly)
- GitHub Actions (monthly)

### labeler.yml

Auto-labels PRs based on changed files:
- `backend` - Changes to backend/
- `frontend` - Changes to frontend/
- `documentation` - Changes to docs/
- `ci/cd` - Changes to workflows/

---

## 📚 Related Documentation

- [Main README](../README.md) - Project overview
- [Contributing Guide](../CONTRIBUTING.md) - Development setup
- [Azure Deployment Guide](../docs/AZURE_DEPLOYMENT_REFERENCE_GUIDE.md) - Deployment reference

---

## 🛠️ Maintenance

When updating configurations:

1. **Workflows**: Test in a branch first with `workflow_dispatch` trigger
2. **Copilot Instructions**: Keep examples current with codebase
3. **Templates**: Update checklists as requirements change
4. **Labels**: Sync `labeler.yml` with actual file structure

---

<p align="center">
  <strong>Secure Renewals HR Portal</strong><br>
  Built with ❤️ for HR teams
</p>
