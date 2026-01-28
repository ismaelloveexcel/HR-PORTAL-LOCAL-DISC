---
name: Maintenance Task
about: Schedule or track routine maintenance
title: '[MAINTENANCE] '
labels: 'maintenance'
assignees: ''

---

## Maintenance Type

- [ ] Dependency updates
- [ ] Security patches
- [ ] Performance optimization
- [ ] Database maintenance
- [ ] Configuration updates
- [ ] Documentation updates
- [ ] Backup verification
- [ ] System cleanup
- [ ] Other (specify below)

## Description
What maintenance needs to be performed?

---

## Scheduling

**Proposed Maintenance Window**:
- **Date**: <!-- e.g., Friday, January 15, 2026 -->
- **Time**: <!-- e.g., 6:00 PM - 10:00 PM GST (Abu Dhabi time) -->
- **Duration**: <!-- Estimated duration -->
- **Impact**: <!-- Will portal be down? Read-only? -->

**User Notification**:
- [ ] Users notified 48 hours in advance
- [ ] Users notified 24 hours in advance
- [ ] Email notification sent
- [ ] Portal banner displayed
- [ ] No notification needed (zero downtime)

---

## Pre-Maintenance Checklist

**Preparation**:
- [ ] Backup database
- [ ] Backup configuration files
- [ ] Document current state
- [ ] Test rollback procedure
- [ ] Prepare rollback plan
- [ ] Notify stakeholders
- [ ] Schedule team availability

**Testing Environment**:
- [ ] Test on staging environment first
- [ ] Verify no breaking changes
- [ ] Document any issues found
- [ ] Update procedure based on testing

---

## Maintenance Steps

<!-- List the specific steps to perform -->

1. <!-- Step 1 -->
2. <!-- Step 2 -->
3. <!-- Step 3 -->

**Commands/Scripts**:
```bash
# Add commands here if applicable
```

---

## Post-Maintenance Verification

**Health Checks** (perform after maintenance):
- [ ] Portal loads successfully
- [ ] Backend health endpoint responds
- [ ] Database connectivity verified
- [ ] Login functionality works
- [ ] Employee data displays correctly
- [ ] UAE compliance features working:
  - [ ] Visa tracking
  - [ ] Emirates ID tracking
  - [ ] Medical fitness alerts
  - [ ] Contract management
- [ ] Reports generate correctly
- [ ] File uploads work
- [ ] Notifications sending

**Performance Checks**:
- [ ] Response times normal
- [ ] No increase in error rates
- [ ] Database queries performing well
- [ ] Memory usage normal

---

## Rollback Plan

**If maintenance fails, rollback steps**:
1. <!-- Rollback step 1 -->
2. <!-- Rollback step 2 -->
3. <!-- Rollback step 3 -->

**Rollback Decision Criteria**:
- [ ] Portal inaccessible for > 15 minutes
- [ ] Critical feature broken
- [ ] Data integrity concerns
- [ ] Security vulnerability introduced
- [ ] Compliance features not working

---

## For Non-Technical Admins

**What This Maintenance Does** (in simple terms):
<!-- Explain what's being updated and why -->

**What You Need To Do**:
- [ ] Approve maintenance window
- [ ] Notify users (template provided below)
- [ ] Monitor during maintenance
- [ ] Test basic functions after maintenance
- [ ] Report any issues immediately

**User Notification Template**:
```
Subject: Scheduled Maintenance - HR Portal

Dear Team,

The HR Portal will undergo scheduled maintenance on [DATE] from [START TIME] to [END TIME] GST.

During this time:
- [Will the portal be available? Yes/No]
- [What features will be affected?]

We appreciate your patience as we improve the system.

Thank you,
HR Team
```

---

## Risk Assessment

**Risk Level**:
- [ ] Low - Routine update, minimal risk
- [ ] Medium - Significant changes, tested on staging
- [ ] High - Major changes, potential for issues

**Mitigation Strategies**:
<!-- How are risks being mitigated? -->

**Contingency Plan**:
<!-- What if something goes wrong? -->

---

## Success Criteria

Maintenance is considered successful when:
- [ ] All planned tasks completed
- [ ] All health checks passing
- [ ] No increase in errors
- [ ] Performance maintained or improved
- [ ] No user-reported issues within 24 hours

---

## Documentation Updates

After maintenance, update:
- [ ] System health documentation
- [ ] Configuration documentation
- [ ] User guides (if features changed)
- [ ] Maintenance log
- [ ] Known issues list

---

## Additional Notes
<!-- Any other relevant information -->

**Related Issues/PRs**:
<!-- Link to related issues or pull requests -->

**References**:
<!-- Link to external documentation, vendor guides, etc. -->
