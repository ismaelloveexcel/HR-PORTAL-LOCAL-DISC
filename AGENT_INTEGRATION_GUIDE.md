# Agent Integration Guide
## How to Use Your Personal Agents

This guide explains how to use the specialized agents created for the HR Portal, including the new **Aesthetic Guardian** and **Technical Guardian** agents.

> **Agent Status:** 
> - ✅ **Deployed as Bots** - Technical Guardian and Aesthetic Guardian now run as automated GitHub Actions workflows
> - 📚 **Also Available as Guidelines** - Agent instruction files can still be used with GitHub Copilot Chat for manual reviews

---

## 🤖 Automated Agent Bots (Active)

### Technical Guardian Bot
**Status:** ✅ Active - Runs automatically

**Automated Monitoring:**
- **Health Checks:** Every 15 minutes
  - Monitors `/api/health/ping` and `/api/health/db`
  - Creates GitHub issues automatically if health checks fail
  - Workflow: `.github/workflows/technical-guardian-health.yml`

- **Security Scans:** Daily at 2 AM UTC + on every PR
  - Scans for vulnerabilities in dependencies (Python & npm)
  - Checks for hardcoded secrets
  - Posts results to PRs and creates issues for critical findings
  - Workflow: `.github/workflows/technical-guardian-security.yml`

### Aesthetic Guardian Bot
**Status:** ✅ Active - Runs on PRs

**Automated Checks:**
- **UI/UX Review:** Triggered on every PR that modifies frontend files
  - Color contrast analysis
  - Responsive design check
  - Loading states verification
  - Button states review
  - Typography consistency
  - Posts detailed review as PR comment
  - Workflow: `.github/workflows/aesthetic-guardian-pr.yml`

---

## Available Agents

### 1. **HR Assistant** (`.github/agents/hr-assistant.md`)
**Purpose:** HR workflows, employee management, compliance, and portal system guidance

**Use when you need to:**
- Import bulk employee data
- Set up onboarding workflows
- Manage contract renewals
- Generate compliance reports
- Understand HR module features

**Example prompts for GitHub Copilot Chat:**
```
"Using the HR Assistant agent instructions, help me import 50 employees from a CSV file"
"With the HR Assistant agent context, how do I set up the probation tracking module?"
"Following HR Assistant guidelines, generate a compliance report for visa expiries"
```

---

### 2. **Portal Engineer** (`.github/agents/portal-engineer.md`)
**Purpose:** Full-stack development, API implementation, database design, bug fixes

**Use when you need to:**
- Add new features (endpoints, components, modules)
- Fix technical bugs
- Design database schemas
- Optimize performance
- Troubleshoot deployment issues

**Example prompts for GitHub Copilot Chat:**
```
"Using the Portal Engineer agent instructions, add a leave management module with approval workflow"
"With the Portal Engineer agent context, fix the slow employee search query"
"Following Portal Engineer guidelines, create a new API endpoint for attendance tracking"
```

---

### 3. **Azure Debugger** (`.github/agents/azure-debugger.md`)
**Purpose:** Azure deployment troubleshooting, CI/CD pipeline fixes

**Use when you need to:**
- Fix failed deployments
- Debug Azure App Service issues
- Resolve GitHub Actions workflow problems
- Troubleshoot database connection issues
- Fix authentication/OIDC problems

**Example prompts for GitHub Copilot Chat:**
```
"Using the Azure Debugger agent instructions, why is my deployment failing with error X?"
"With the Azure Debugger agent context, the app is deployed but returns 502 errors"
"Following Azure Debugger guidelines, database migrations are not running"
```

---

### 4. **Azure Deployment Engineer** (`.github/agents/azure-deployment-engineer.md`)
**Purpose:** End-to-end Azure setup, infrastructure as code, deployment automation

**Use when you need to:**
- Set up Azure infrastructure from scratch
- Configure CI/CD pipelines
- Implement deployment slots
- Set up monitoring and alerts
- Automate infrastructure management

**Example prompts for GitHub Copilot Chat:**
```
"Using the Azure Deployment Engineer agent instructions, set up a new production environment"
"With the Azure Deployment Engineer agent context, implement blue-green deployment"
"Following Azure Deployment Engineer guidelines, configure Application Insights"
```

---

### 5. **Code Quality Monitor** (`.github/agents/code-quality-monitor.md`)
**Purpose:** Security scanning, code quality checks, vulnerability detection

**Use when you need to:**
- Scan for security vulnerabilities
- Check code quality metrics
- Find performance issues
- Detect code smells
- Review dependency security

**Example prompts for GitHub Copilot Chat:**
```
"Using the Code Quality Monitor agent instructions, scan the codebase for security issues"
"With the Code Quality Monitor agent context, check if our dependencies have vulnerabilities"
"Following Code Quality Monitor guidelines, review the code quality of the new feature"
```

---

### 6. **Aesthetic Guardian** ⭐ DEPLOYED BOT (`.github/agents/aesthetic-guardian.md`)
**Purpose:** UI/UX quality, visual consistency, accessibility, design improvements

**🤖 Automated Bot Features:**
- ✅ **UI/UX review** on every PR with frontend changes (automatic)
- ✅ **Color contrast analysis** (automatic)
- ✅ **Responsive design check** (automatic)
- ✅ **Loading states verification** (automatic)
- ✅ **PR comments** with design recommendations (automatic)

**Manual Use with GitHub Copilot Chat:**
```
"Using the Aesthetic Guardian agent instructions, review the employee dashboard design"
"With the Aesthetic Guardian agent context, check accessibility compliance for the login page"
"Following Aesthetic Guardian guidelines, suggest improvements for the employee list view"
"Using Aesthetic Guardian agent, find GitHub examples of modern HR dashboards"
```

**What this agent checks (automatically on PRs):**
- Color contrast issues and accessibility
- Responsive design classes (sm:, md:, lg:, xl:)
- Missing loading states in async components
- Button interactive states (hover, focus, disabled)
- Typography consistency across files

---

### 7. **Technical Guardian** ⭐ DEPLOYED BOT (`.github/agents/technical-guardian.md`)

### 8. **My Agent** (`.github/agents/my-agent.agent.md`)
**Purpose:** Custom deployment guardrails for “my agent” aligned to the Azure OIDC pattern.

**Use when you need:**
- To run or review “my agent” deployments
- To prevent OIDC token failures
- To confirm required secrets and workflow steps
**Purpose:** System health monitoring, proactive issue detection, automated fixes

**🤖 Automated Bot Features:**
- ✅ **Health monitoring** every 15 minutes (automatic)
- ✅ **Security scans** daily + on PRs (automatic)
- ✅ **Issue creation** when problems detected (automatic)
- ✅ **PR comments** with security scan results (automatic)

**Manual Use with GitHub Copilot Chat:**
```
"Using the Technical Guardian agent instructions, analyze the system health"
"With the Technical Guardian agent context, analyze API performance metrics"
"Following Technical Guardian guidelines, check for database optimization opportunities"
"Using Technical Guardian agent, review the code for security vulnerabilities"
```

**What this agent monitors (automatically):**
- Health endpoint status (every 15 min)
- Database connectivity (every 15 min)
- Security vulnerabilities (daily + PRs)
- Dependency vulnerabilities (daily + PRs)
- Hardcoded secrets (daily + PRs)

---

## How Agents Work Together

> **Note:** These workflows show how to use agents with GitHub Copilot Chat. Replace `"Using [Agent] agent instructions"` prompts with your actual questions/tasks in GitHub Copilot Chat while referencing the agent instruction files.

### Example Workflow 1: Adding a New Feature

**Step 1:** Planning with HR Assistant (in GitHub Copilot Chat)
```
"Using the HR Assistant agent instructions, I want to add employee performance reviews. 
What features should I include?"
```
→ GitHub Copilot (with HR Assistant context) provides requirements and workflow design

**Step 2:** Implementation with Portal Engineer
```
"Using the Portal Engineer agent instructions, implement the performance review module 
based on the requirements discussed"
```
→ GitHub Copilot (with Portal Engineer context) helps create backend APIs and frontend components

**Step 3:** Design Review with Aesthetic Guardian
```
"Using the Aesthetic Guardian agent instructions, review the performance review UI 
and suggest improvements"
```
→ GitHub Copilot (with Aesthetic Guardian context) ensures design quality and consistency

**Step 4:** Quality Check with Technical Guardian
```
"Using the Technical Guardian agent instructions, scan the new performance review code 
for issues"
```
→ GitHub Copilot (with Technical Guardian context) checks security, performance, and code quality

**Step 5:** Code Review with Code Quality Monitor
```
"Using the Code Quality Monitor agent instructions, review the performance review pull request"
```
→ GitHub Copilot (with Code Quality Monitor context) ensures best practices

**Step 6:** Deployment with Azure Deployment Engineer
```
"Using the Azure Deployment Engineer agent instructions, deploy the performance review feature 
to production"
```
→ GitHub Copilot (with Azure Deployment Engineer context) handles the deployment

---

### Example Workflow 2: Fixing a Performance Issue

**Step 1:** Manual Detection or Investigation
```
"API endpoint /api/employees is taking 3.2 seconds - this needs investigation"
```

**Step 2:** Investigation with Technical Guardian
```
"Using the Technical Guardian agent instructions, analyze why /api/employees is slow"
```
→ Identifies N+1 query problem and missing database index

**Step 3:** Fix Implementation with Portal Engineer
```
"Using the Portal Engineer agent instructions, fix the slow employee query based on 
the identified N+1 query problem"
```
→ GitHub Copilot helps implement the fix

**Step 4:** Verification with Technical Guardian
```
"Using the Technical Guardian agent instructions, verify the performance improvement"
```
→ Confirms query now takes <100ms

---

### Example Workflow 3: UI/UX Improvement

**Step 1:** Manual Review or Audit
```
"The employee dashboard has inconsistent spacing and missing empty states"
```

**Step 2:** Get Recommendations with Aesthetic Guardian
```
"Using the Aesthetic Guardian agent instructions, show me modern examples of employee 
dashboards from GitHub and suggest improvements"
```
→ Provides links to high-quality examples with analysis

**Step 3:** Implementation with Portal Engineer
```
"Using the Portal Engineer agent instructions, implement the dashboard improvements 
suggested"
```

**Step 4:** Accessibility Check with Aesthetic Guardian
```
"Using the Aesthetic Guardian agent instructions, verify the updated dashboard meets 
WCAG 2.1 AA standards"
```

---

## How to Use Agents

> **Important:** These agents are instruction files for GitHub Copilot Chat, not autonomous bots. They do not automatically monitor, create issues, or execute actions.

### Method 1: GitHub Copilot Chat in VS Code
1. Open GitHub Copilot Chat in VS Code
2. Reference the agent file you want to use
3. Ask your question or request

```
"Using the [Agent Name] agent instructions in .github/agents/, [your request]"
```

### Method 2: GitHub Copilot Chat in GitHub
1. Open a PR or issue
2. Use GitHub Copilot in the web interface
3. Reference the agent instructions

```
"Following the Technical Guardian agent guidelines, review this code for security issues"
```

### Method 3: Manual Reference
Open the agent markdown file and follow the guidelines manually for code reviews and implementation decisions.

---

## Creating Automated Workflows (Optional)

If you want to create actual automated monitoring, you'll need to build GitHub Actions workflows or other automation tools. The agent files provide the guidelines and standards to implement in your automation.

Example: Automated health check workflow
```yaml
name: System Health Check
on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check API Health
        run: |
          curl -f https://your-app.azurewebsites.net/api/health/ping || exit 1
      
      - name: Create Issue on Failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 Health Check Failed',
              body: 'The health endpoint is not responding. Check logs immediately.',
              labels: ['critical', 'automated']
            })
```
---

## Best Practices

### 1. **Choose the Right Agent for Your Task**
- UI/design issues → **Aesthetic Guardian**
- Technical/performance issues → **Technical Guardian**
- New features → **Portal Engineer** + **HR Assistant**
- Deployment problems → **Azure Debugger**
- Infrastructure setup → **Azure Deployment Engineer**
- Security/quality → **Code Quality Monitor**

### 2. **Provide Context in Your Prompts**
Good prompt for GitHub Copilot Chat:
```
"Using the Portal Engineer agent instructions, add a leave management module with:
- Multiple leave types (annual, sick, emergency)
- Approval workflow (employee → manager → HR)
- Leave balance tracking
- Calendar view"
```

Bad prompt:
```
"add leaves"
```

### 3. **Use Agents Sequentially for Complex Tasks**
For complex tasks, consult agents in this order:
1. Planning → **HR Assistant**
2. Implementation → **Portal Engineer**
3. Design review → **Aesthetic Guardian**
4. Technical review → **Technical Guardian**
5. Deployment → **Azure Deployment Engineer**

### 4. **Reference Multiple Agents**
You can reference multiple agent guidelines in one session:
```
"Using the Portal Engineer and Aesthetic Guardian agent instructions, 
implement a new feature that follows our design standards"
```

---

## Understanding Agent Reports and Monitoring

> **Note:** The following sections describe what you could implement using the agent guidelines, not automatic features that currently exist.

### 1. **Manual Reviews Based on Agent Guidelines**

You can use the **Technical Guardian** guidelines to create manual daily checks:
```
Daily System Health Checklist (based on Technical Guardian):
- Check API Response Time: Target <150ms (avg)
- Review Error Rate: Target <0.1%
- Review Database Query Performance for slow queries
- Check for Security vulnerabilities
- Review and act on recommendations
```

You can use the **Aesthetic Guardian** guidelines for weekly design audits:
```
Weekly Design Audit Checklist (based on Aesthetic Guardian):
- Check Accessibility Score: Target >90/100
- Review Design Consistency across pages
- Check Performance Score: Target >90/100
- Review and implement design recommendations
```

### 2. **Implementing Automated Monitoring (Optional)**
Agents automatically create issues:
```
Issue #123 (created by Technical Guardian)
🔧 Slow Query Detected: get_employees_by_department

Severity: Medium
Query Time: 3.2s → Should be <200ms
Recommended Fix: Add index on department column
```

### 3. **Pull Requests**


If you want automated monitoring and issue creation (following the agent guidelines), you would need to build workflows like this:

```yaml
name: Automated Technical Check
on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM

jobs:
  tech-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check for slow queries
        run: |
          # Your logic to check query performance
          # Based on Technical Guardian guidelines
          
      - name: Create issue if problems found
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🔧 Slow Query Detected',
              body: 'Automated check found queries exceeding performance targets.',
              labels: ['performance', 'automated']
            })
```

---

## Customizing Agent Guidelines

### Modify Agent Instructions

Edit the agent markdown files to match your needs:

```markdown
# In .github/agents/aesthetic-guardian.md

## Customization: Company Branding

Primary Colors:
- Brand Blue: #0066CC (change this to your brand color)
- Success Green: #10B981
- Error Red: #EF4444

Typography:
- Headings: Montserrat (change to your preferred font)
- Body: Inter
```

### Add Custom Rules

```markdown
# In .github/agents/technical-guardian.md

## Custom Rules

### Performance Targets
- API endpoints must respond in <200ms (was <500ms)
- Database queries must complete in <50ms (was <100ms)
```

---

## Troubleshooting

### Can't Use Agents in GitHub Copilot?
1. Make sure agent files exist in `.github/agents/`
2. Reference the full path when prompting
3. Check that GitHub Copilot has access to the repository

### Agent Guidelines Don't Match Your Needs?
1. Edit the agent markdown files
2. Add project-specific guidelines
3. Remove sections that don't apply

### Want Automation Instead of Guidelines?
Build GitHub Actions workflows that implement the agent logic. See "Implementing Automated Monitoring" section above.

---

## Quick Reference Card

| Task | Agent | How to Use in GitHub Copilot Chat |
|------|-------|----------------------------------|
| Import employees | HR Assistant | "Using HR Assistant agent instructions, help import employees from CSV" |
| Add new feature | Portal Engineer | "Using Portal Engineer agent instructions, add [feature]" |
| Fix deployment | Azure Debugger | "Using Azure Debugger agent instructions, fix deployment error" |
| Review design | Aesthetic Guardian | "Using Aesthetic Guardian agent instructions, review [component]" |
| Check security | Technical Guardian | "Using Technical Guardian agent instructions, security scan" |
| Optimize performance | Technical Guardian | "Using Technical Guardian agent instructions, optimize [endpoint]" |
| Deploy to Azure | Azure Deployment Engineer | "Using Azure Deployment Engineer agent instructions, deploy" |
| Code review | Code Quality Monitor | "Using Code Quality Monitor agent instructions, review PR" |

---

## Getting Started

### Quick Start Guide

**Step 1:** Familiarize yourself with agent files
```bash
# View available agents
ls .github/agents/

# Read an agent file
cat .github/agents/aesthetic-guardian.md
```

**Step 2:** Try using an agent with GitHub Copilot Chat
```
# In VS Code or GitHub Copilot Chat:
"Using the Aesthetic Guardian agent instructions, review the login page design"

"Using the Technical Guardian agent instructions, check system health status"
```

**Step 3:** Use agents in your development workflow
- Reference agent guidelines when making design decisions
- Use agents with GitHub Copilot for code reviews
- Follow agent standards for new features

---

## Support

### Need Help?
1. **Check agent documentation** in `.github/agents/`
2. **Review examples** in this guide
3. **Use GitHub Copilot Chat** with agent instructions:
   ```
   "Using the HR Assistant agent instructions, how do I use these agents effectively?"
   ```

### Found a Bug?
Report issues with agent behavior:
```
Title: Agent Bug: Technical Guardian not detecting slow queries
Body: 
@technical-guardian is not detecting the slow query in 
/api/employees. The query takes 5 seconds but no issue was created.

Expected: Issue should be auto-created
Actual: No issue created
```

---

**Last Updated:** January 20, 2026  
**Version:** 1.0  
**Maintained by:** Azure System Engineer
