# GitHub Copilot Agents

This directory contains specialized GitHub Copilot agents designed to assist with the Secure Renewals HR Portal development and operations.

## 🤖 Available Agents

### 1. [HR Assistant](hr-assistant.md) — see [Agent Governance](../../AGENT_GOVERNANCE.md)
Expert HR Assistant and Portal System Engineer for solo HR professionals.

**Use when you need**:
- HR workflow guidance
- Feature planning
- Module discovery
- Automation ideas
- Compliance advice

### 2. [Portal Engineer](portal-engineer.md) — see [Agent Governance](../../AGENT_GOVERNANCE.md)
Expert technical implementation specialist for full-stack development.

**Use when you need**:
- Feature implementation
- Code examples
- Architecture guidance
- Bug fixes
- Performance optimization

### 3. [Code Quality Monitor](code-quality-monitor.md) — see [Agent Governance](../../AGENT_GOVERNANCE.md)
Proactive code quality and security scanner.

**Use when you need**:
- Security scans
- Code quality checks
- Performance analysis
- Best practices
- Issue detection

### 4. [Azure Deployment Specialist](azure-deployment-specialist.md) — see [Agent Governance](../../AGENT_GOVERNANCE.md)
**NEW!** Expert in Azure deployment, repository history, and troubleshooting.

**Use when you need**:
- Azure deployment through VS Code
- GitHub Actions deployment setup
- Login/authentication troubleshooting
- Database connection issues
- Python environment problems
- Complete repository knowledge
- Emergency recovery procedures

### 5. [Azure Debugging Engineer](azure-debugger.md) — see [Agent Governance](../../AGENT_GOVERNANCE.md)
**AUTOMATED FIX ENGINE** - Expert in automated diagnosis and resolution of Azure deployment failures.

**Use when you need**:
- Automatic analysis of deployment failures
- Bicep template fixes
- GitHub Actions workflow debugging
- Backend startup issues
- Database connection failures
- CORS configuration problems
- OIDC authentication fixes
- Automated PR creation with fixes
- Production deployment recovery

### 6. [My Agent](my-agent.agent.md)
Custom deployment guardrails for “my agent” (OIDC permissions, required secrets, workflow use).

### 7. [HR Portal Finalizer & Auditor](hr-portal-finalizer.agent.md) — **NEW!** Autonomous MVP Finisher
**AUTONOMOUS MODE** - Sole owner and finisher of the HR Portal MVP for a non-technical solo HR user.

**Use when you need**:
- Urgent MVP completion
- Autonomous execution without waiting for instructions
- Employee module completion (source of truth)
- Pass generation (dynamic, visible)
- ESS workflow implementation (leave, document requests)
- Dashboard & navigation
- UAE compliance (visa tracking, alerts)
- Deployment health checks
- Blueprint-guided pragmatic decisions

**Quick Commands**:
- `begin` - Start default MVP sequence
- `status` - Show MVP progress tracker
- `employees` - Focus on employee module
- `passes` - Focus on pass generation
- `ess` - Focus on ESS flows
- `compliance` - Focus on UAE compliance
- `deploy` - Focus on deployment health
- `audit` - Run full codebase audit

## 📖 Documentation

- **[Quick Reference](QUICK_REFERENCE.md)** - Fast lookup for common tasks
- **[Configuration](config.yml)** - Agent settings and rules
- **[Full Guide](../../docs/COPILOT_AGENTS.md)** - Complete documentation
- **[Deployment Guide](../../docs/AGENT_DEPLOYMENT_GUIDE.md)** - How to deploy and use agents

## 🚀 Getting Started

### Already Deployed!
The agents are markdown files - they work automatically once this repo is cloned. No installation needed!

### Using the Agents
1. **Identify your need** - HR task, technical implementation, or quality check?
2. **Choose an agent** - Open the relevant agent file in your IDE
3. **Ask questions** - Use GitHub Copilot with agent context
4. **Follow guidance** - Implement the recommendations

**📖 Need detailed setup instructions?** See [Deployment Guide](../../docs/AGENT_DEPLOYMENT_GUIDE.md)

## 💡 Example Usage

### Planning a Feature
```
1. Open: hr-assistant.md
2. Ask: "Help me plan an onboarding module"
3. Get: Requirements, workflow, automation ideas
```

### Implementing Code
```
1. Open: portal-engineer.md
2. Ask: "Create API endpoints for onboarding"
3. Get: Complete code following portal patterns
```

### Checking Quality
```
1. Open: code-quality-monitor.md
2. Ask: "Scan for security issues"
3. Get: Issues found with fix recommendations
```

## 🔄 Typical Workflow

```
Design & Plan (Guardian HR-UAE)
  ↓
Research (OSS Scout)
  ↓
Plan Details (HR Assistant)
  ↓
Implement (Portal Engineer)
  ↓
Verify (Code Quality Monitor)
  ↓
Compliance Review (Guardian HR-UAE)
  ↓
Deploy (Azure Deployment Specialist)
  ↓
Debug & Fix (Azure Debugging Engineer)
  ↓
Live ✅
```

### 🚀 Urgent MVP Completion Workflow

```
Invoke HR Portal Finalizer
  ↓
Auto-scan repo + blueprint
  ↓
Prioritized plan with deviations
  ↓
Deliver ready code/config
  ↓
Minimal clarifications (if blocked)
  ↓
MVP Complete ✅
```

## 🎯 Quick Commands

| Task | Agent | Command |
|------|-------|---------|
| Plan feature | HR Assistant | "Help me plan [feature]" |
| Find modules | HR Assistant | "Find [module] on GitHub" |
| Create API | Portal Engineer | "Create API for [feature]" |
| Build component | Portal Engineer | "Create React component for [feature]" |
| Security scan | Code Monitor | "Scan for security issues" |
| Check quality | Code Monitor | "Review code quality" |
| Deploy to Azure | Azure Deployment | "Deploy to Azure App Service" |
| Fix login issues | Azure Deployment | "Troubleshoot login errors" |
| Fix database | Azure Deployment | "Debug database connection" |
| Auto-fix deployment | Azure Debugger | "Analyze and fix deployment failures" |
| Fix Bicep errors | Azure Debugger | "Fix Bicep validation failures" |
| Resolve CORS | Azure Debugger | "Fix CORS configuration" |
| UAE compliance check | Guardian HR-UAE | "Check UAE labour law compliance for [feature]" |
| Design HR workflow | Guardian HR-UAE | "Design workflow for [process]" |
| Digital pass design | Guardian HR-UAE | "Create digital pass for [request type]" |
| Quality scoring | Guardian HR-UAE | "Score this implementation" |
| Search GitHub repos | OSS Scout | "Find open-source [module] for HR" |
| Evaluate repo | OSS Scout | "Evaluate [repo] for UAE HR use" |
| **Urgent MVP finish** | **HR Portal Finalizer** | "begin" or "finish MVP" |
| MVP status | HR Portal Finalizer | "status" |
| Fix employees | HR Portal Finalizer | "employees" |
| Generate passes | HR Portal Finalizer | "passes" |
| ESS workflows | HR Portal Finalizer | "ess" |
| UAE compliance | HR Portal Finalizer | "compliance" |
| Full audit | HR Portal Finalizer | "audit" |

## 📊 Agent Specializations

```
HR Assistant
├── HR Operations ✅
├── Workflow Automation ✅
├── Module Discovery ✅
└── Compliance ✅

Portal Engineer
├── Backend Development ✅
├── Frontend Development ✅
├── Database Design ✅
└── DevOps ✅

Code Quality Monitor
├── Security Scanning ✅
├── Performance Analysis ✅
├── Code Quality ✅
└── Best Practices ✅

Azure Deployment Specialist
├── Azure App Service ✅
├── GitHub Actions ✅
├── VS Code Deployment ✅
├── Login Troubleshooting ✅
├── Database Issues ✅
└── Python Environment ✅

Azure Debugging Engineer
├── Automated Failure Analysis ✅
├── Bicep Template Fixes ✅
├── GitHub Actions Debugging ✅
├── Backend Startup Issues ✅
├── Database Connectivity ✅
├── CORS & Networking ✅
├── OIDC Authentication ✅
└── Automated PR Creation ✅

Guardian HR-UAE
├── UAE Labour Law Compliance ✅
├── HR Systems Engineering ✅
├── Process Architecture ✅
├── Quality Scoring ✅
├── Digital Pass Design ✅
├── Aesthetic Constraints ✅
├── Microsoft Integration ✅
└── Compliance Summaries ✅

OSS Scout
├── GitHub Repository Search ✅
├── Module Evaluation ✅
├── License Analysis ✅
├── Adaptation Planning ✅
└── UAE Compliance Awareness ✅

HR Portal Finalizer
├── Autonomous MVP Execution ✅
├── Employee Module Completion ✅
├── Pass Generation ✅
├── ESS Workflow Implementation ✅
├── Dashboard & Navigation ✅
├── UAE Compliance Tracking ✅
├── Deployment Health ✅
├── Blueprint Interpretation ✅
└── Pragmatic Decision Making ✅
```

## 🛠️ Integration

Agents integrate with:
- GitHub Copilot
- GitHub Actions (CI/CD)
- Pull Request reviews
- Issue tracking
- Development workflow

## 📈 Success Metrics

Using agents effectively results in:
- ⏱️ 30-50% faster feature development
- 🐛 60% fewer bugs reaching production
- 🔒 80% better security posture
- 📚 100% better documentation
- 💡 Continuous team learning

## 🆘 Need Help?

1. Start with [Quick Reference](QUICK_REFERENCE.md)
2. Read the [Full Guide](../../docs/COPILOT_AGENTS.md)
3. Open specific agent file for detailed help
4. Ask questions with context

## 🔄 Updates

Agents are living documents. Update them when:
- New patterns emerge
- Best practices evolve
- Features are added
- Lessons are learned

## 📝 Contributing

To improve agents:
1. Identify gaps in agent knowledge
2. Add new examples and patterns
3. Update with lessons learned
4. Test changes with real scenarios

## 🔗 Related Resources

- [HR User Guide](../../docs/HR_USER_GUIDE.md)
- [System Health Check](../../docs/SYSTEM_HEALTH_CHECK.md)
- [Implementation Plan](../../docs/HR_IMPLEMENTATION_PLAN.md)
- [Recommended Add-ons](../../docs/RECOMMENDED_ADDONS.md)

---

**Remember**: These agents are your partners in building and maintaining the HR Portal. Use them often!
