# Rollback & Recovery Guide

> **Emergency procedures** for non-technical HR admins when deployments fail

---

## 🚨 When to Use This Guide

Use this guide when:
- Portal is down or completely broken after a deployment
- Critical features stopped working after an update
- Data appears corrupted or missing
- Security vulnerability was introduced
- Health checks are failing repeatedly

**⚠️ Important**: Only rollback when absolutely necessary. Many issues can be fixed forward rather than rolling back.

---

## 📋 Quick Decision Tree

```
Portal has issues after deployment
   ↓
Is portal completely unusable?
   YES → Immediate Rollback (Section A)
   NO → ↓

Is a critical feature broken?
   YES → Can you work around it temporarily?
      YES → Fix Forward (Section B)
      NO → Quick Rollback (Section C)
   NO → ↓

Is it a minor issue?
   YES → Fix Forward (Section B)
   NO → Evaluate (Section D)
```

---

## Section A: Immediate Rollback (Portal Down)

### Symptoms
- Portal returns 404, 500, or other error
- Cannot log in at all
- Blank/white screen
- Complete data loss

### Steps for Non-Technical Admin

**1. Confirm It's Not Just You**
```
- Try different browser
- Try different device/network
- Ask colleague to try
- Check if Azure is having issues
```

**2. Check Health Status**
```
GitHub → Actions → Look for red X next to recent deployment
```

**3. Notify Stakeholders Immediately**
```
Subject: HR Portal Temporarily Unavailable

The HR portal is temporarily unavailable due to a technical issue.
We're working on restoration.

Estimated downtime: [1-2 hours]
Updates will be provided every 30 minutes.

For urgent HR matters, contact [backup contact].
```

**4. Contact Technical Support** (if available)
Provide them:
- When issue started
- What changed (recent deployment)
- Health check results
- Screenshots of errors

**5. Self-Service Rollback** (if no technical support available)

Go to GitHub repository:
```
1. Click "Actions" tab
2. Find "Deploy to Azure" or deployment workflow
3. Look for last successful run (green checkmark)
4. Click on that successful run
5. Click "Re-run jobs" button (top right)
6. Wait 5-10 minutes
7. Test portal
```

**6. Verify Restoration**
```
[ ] Can log in
[ ] Employee list loads
[ ] Compliance features work
[ ] Documents accessible
[ ] Reports generate
```

**7. Post-Incident**
```
- Document what happened
- Note time of outage
- Create GitHub issue with details
- Schedule post-mortem (if team)
```

---

## Section B: Fix Forward (Preferred Approach)

### When to Fix Forward
- Portal is still usable
- Only specific feature is broken
- Workaround exists
- Issue is understood and fixable

### Advantages of Fix Forward
✅ Faster than rollback  
✅ Keeps recent improvements  
✅ Less disruptive  
✅ Learning opportunity

### Steps

**1. Identify Exact Issue**
```
What's broken:
- Specific feature/page
- Error message (exact text)
- When it occurs
- Who is affected
```

**2. Check if Workaround Exists**
```
Can users:
- Use alternative feature?
- Access via different path?
- Wait until fixed?
```

**3. Create GitHub Issue**
```
Title: [BUG] Brief description
Labels: bug, high-priority

Include:
- What's broken
- How to reproduce
- Impact on operations
- Workaround (if any)
```

**4. Implement Quick Fix**
```
If you can:
- Revert specific change
- Update configuration
- Disable broken feature temporarily

If you can't:
- Assign to developer
- Set priority
- Communicate workaround to users
```

**5. Monitor**
```
- Watch for fix deployment
- Test immediately when deployed
- Verify issue resolved
- Update users
```

---

## Section C: Quick Rollback (Broken Critical Feature)

### When to Use
- Visa tracking broken (UAE compliance at risk)
- Login system broken (users locked out)
- Data corruption detected
- Security vulnerability introduced

### Rollback Decision Criteria

**Rollback if ANY of these are true**:
- ❌ Compliance features broken (visa, EID, contracts)
- ❌ Data loss or corruption
- ❌ Security vulnerability
- ❌ Users completely blocked from work
- ❌ Fix will take > 4 hours

**Don't rollback if**:
- ✅ Minor UI issue
- ✅ Non-critical feature broken
- ✅ Workaround available
- ✅ Fix available within 1-2 hours

### Rollback Procedure

**Method 1: Via GitHub Actions (Recommended)**

```bash
1. Go to GitHub repository → Actions tab
2. Find "Deploy to Azure" workflow
3. Look at recent runs
4. Find last known good deployment (green checkmark)
5. Click on that run
6. Click "Re-run jobs" button
7. Confirm re-run
8. Monitor deployment (5-10 minutes)
9. Test portal thoroughly
```

**Method 2: Via Git (For Technical Users)**

```bash
# List recent deployments
git log --oneline -n 10

# Find the commit before the problematic one
# Let's say problematic commit is abc1234
# And good commit is xyz5678

# Revert to good commit
git revert abc1234

# Or reset to good commit (use with caution)
git reset --hard xyz5678

# Push (requires force push privileges)
git push origin main --force
```

**Method 3: Via Azure Portal (If GitHub unavailable)**

```
1. Go to Azure Portal
2. Find your App Service
3. Go to Deployment Center
4. Find "Previous deployments" or "Deployment history"
5. Select last working deployment
6. Click "Redeploy"
7. Wait for completion
8. Test portal
```

---

## Section D: Evaluation & Decision Making

### Severity Assessment

**Critical (Rollback Immediately)**:
- Portal completely down
- Data loss/corruption
- Security breach
- UAE compliance features broken
- No workaround available

**High (Rollback Within 1 Hour)**:
- Major feature broken
- Many users affected
- Workaround is complex
- Business operations blocked

**Medium (Fix Forward)**:
- Single feature broken
- Simple workaround exists
- Only some users affected
- Not compliance-related

**Low (Schedule Fix)**:
- Minor UI issues
- Cosmetic problems
- Documentation out of date
- No operational impact

### Impact Assessment

**Questions to Ask**:
1. How many users are affected?
   - All users → High priority
   - Some users → Medium priority
   - Few users → Low priority

2. Is UAE compliance at risk?
   - Yes → Immediate action
   - No → Standard priority

3. Can work continue?
   - No → Critical
   - With difficulty → High
   - Yes, normally → Low

4. How long to fix?
   - > 4 hours → Consider rollback
   - 1-4 hours → Fix forward or rollback
   - < 1 hour → Fix forward

### Decision Matrix

| Severity | Compliance Risk | Users Affected | Action |
|----------|----------------|----------------|--------|
| Critical | Yes | All | Immediate Rollback |
| Critical | No | All | Immediate Rollback |
| High | Yes | Many | Quick Rollback |
| High | No | Many | Evaluate (likely rollback) |
| Medium | Yes | Some | Quick fix or rollback |
| Medium | No | Some | Fix forward |
| Low | Any | Any | Fix forward |

---

## 🔄 Rollback Verification Checklist

After any rollback, verify:

### Core Functionality
- [ ] Portal URL accessible
- [ ] Login system works
- [ ] Dashboard loads
- [ ] Navigation works

### Employee Data
- [ ] Employee list displays
- [ ] Can view employee details
- [ ] Can edit employee records
- [ ] Search functionality works
- [ ] Filters work correctly

### UAE Compliance (Critical)
- [ ] Visa tracking displays correctly
- [ ] Visa expiry dates accurate
- [ ] Emirates ID tracking works
- [ ] Medical fitness tracking works
- [ ] Contract information displays
- [ ] Compliance alerts showing
- [ ] Alert calculations correct

### Documents
- [ ] Can view uploaded documents
- [ ] Can upload new documents
- [ ] Documents display correctly
- [ ] Download works

### Reports
- [ ] Can generate employee report
- [ ] Can generate compliance report
- [ ] Export to Excel works
- [ ] Reports contain correct data

### Performance
- [ ] Page load time < 3 seconds
- [ ] No console errors (check browser console)
- [ ] No visible errors on page

---

## 📧 Communication Templates

### Template 1: Incident Notification

```
Subject: [URGENT] HR Portal Temporarily Unavailable

Team,

The HR Portal is currently unavailable due to a technical issue following a system update.

Status: Under investigation
Estimated restoration: [Time]

What this means:
- You cannot access the portal right now
- Your data is safe and backed up
- We're working on restoration

For urgent HR matters during this time:
- Contact: [Name/Email]
- Or: [Alternative contact]

Updates will be provided every 30 minutes.

Thank you for your patience.
```

### Template 2: Restoration Notification

```
Subject: HR Portal Restored - Back Online

Team,

The HR Portal has been restored and is now fully operational.

Duration of outage: [X hours]
Issue: [Brief explanation]
Resolution: [What was done]

What to do now:
1. Clear your browser cache (Ctrl+F5)
2. Log in as normal
3. Verify your recent work is intact
4. Report any issues immediately

We apologize for the inconvenience.

Note: We've implemented additional monitoring to prevent similar issues.
```

### Template 3: Partial Service Notification

```
Subject: HR Portal - Temporary Workaround for [Feature]

Team,

The [feature name] is temporarily unavailable following a system update.

What's affected: [Specific feature]
What still works: [List working features]

Temporary workaround:
[Step-by-step workaround]

Estimated fix: [Timeline]

All other features are working normally. Your data is safe.

For urgent [feature] needs:
- Contact: [Alternative method]

Thank you for your understanding.
```

---

## 🔍 Post-Rollback Actions

### Immediate (Within 1 Hour)
1. **Verify restoration** using checklist above
2. **Notify users** of restoration
3. **Document incident** in GitHub issue
4. **Review what went wrong**

### Short-term (Within 24 Hours)
1. **Analyze root cause**
   - What changed?
   - Why did it break?
   - What was missed in testing?

2. **Create prevention plan**
   - What test should be added?
   - What monitoring needed?
   - What documentation to update?

3. **Update stakeholders**
   - Send post-incident report
   - Explain prevention measures
   - Timeline for proper fix

### Long-term (Within 1 Week)
1. **Implement proper fix**
   - Address root cause
   - Add tests
   - Document solution

2. **Update processes**
   - Improve testing checklist
   - Enhance monitoring
   - Update deployment process

3. **Train team** (if applicable)
   - Share lessons learned
   - Update documentation
   - Practice recovery procedures

---

## 🛡️ Prevention Strategies

### Before Deployment
- [ ] Test on staging environment first
- [ ] Review all automated checks
- [ ] Check compliance features specifically
- [ ] Verify database migrations are reversible
- [ ] Have rollback plan ready
- [ ] Schedule during low-usage time
- [ ] Notify users in advance

### During Deployment
- [ ] Monitor health checks
- [ ] Watch error logs
- [ ] Have team available
- [ ] Test critical features immediately
- [ ] Keep rollback instructions handy

### After Deployment
- [ ] Run verification checklist
- [ ] Monitor for 1-2 hours
- [ ] Check user feedback
- [ ] Review error rates
- [ ] Document any issues

---

## 🆘 Emergency Contacts

### Technical Issues
- **Primary**: [Technical Support Email/Phone]
- **Secondary**: [Backup Contact]
- **After Hours**: [Emergency Contact]

### Business Issues
- **HR Leadership**: [Contact]
- **IT Management**: [Contact]
- **CEO/Management** (for critical outages): [Contact]

### External Support
- **Azure Support**: [Support plan level]
- **GitHub Support**: [If applicable]
- **Database Administrator**: [If external]

---

## 📚 Additional Resources

- [System Health Check](SYSTEM_HEALTH_CHECK.md) - System status
- [Deployment Guide](GITHUB_DEPLOYMENT_OPTIONS.md) - Deployment procedures
- [Copilot Agent System Guide](COPILOT_AGENT_SYSTEM_GUIDE.md) - Automated checks
- [Contributing Guide](../CONTRIBUTING.md) - Development processes
- [Security Policy](../SECURITY.md) - Security procedures

---

## 🎓 Learning from Incidents

### Post-Incident Review Template

```markdown
## Incident Report: [Date]

### Summary
- **Date/Time**: [When it occurred]
- **Duration**: [How long]
- **Impact**: [Who/what was affected]
- **Severity**: [Critical/High/Medium/Low]

### Timeline
- [Time] - Issue detected
- [Time] - Notification sent
- [Time] - Rollback initiated
- [Time] - Service restored
- [Time] - Root cause identified

### Root Cause
[What caused the issue]

### Resolution
[How it was fixed]

### Prevention
- [ ] Test added
- [ ] Monitoring added
- [ ] Documentation updated
- [ ] Process improved

### Lessons Learned
[What we learned and will do differently]
```

---

**Remember**: Rollback is a tool, not a failure. It's better to rollback quickly than to struggle with a broken system. Your priority is keeping the HR portal operational for your team.

---

**Guide Version**: 1.0  
**Last Updated**: January 2026  
**Next Review**: After first rollback incident
