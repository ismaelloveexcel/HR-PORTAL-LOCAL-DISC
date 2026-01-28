# HR Portal FAQ - Frequently Asked Questions

> **Quick answers** for solo HR operators in Abu Dhabi startups

---

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Account & Access](#account--access)
- [Employee Management](#employee-management)
- [UAE Compliance](#uae-compliance)
- [Documents & Files](#documents--files)
- [Reports & Analytics](#reports--analytics)
- [Troubleshooting](#troubleshooting)
- [System Maintenance](#system-maintenance)
- [Security & Privacy](#security--privacy)
- [Automated Reviews & Copilot](#automated-reviews--copilot)

---

## Getting Started

### Q: What is this HR Portal for?
**A**: This is an internal application for managing employee records, tracking UAE compliance requirements (visa, Emirates ID, contracts), and handling HR operations for startups in Abu Dhabi with solo HR teams.

### Q: Do I need technical knowledge to use this?
**A**: No! The portal is designed for non-technical HR administrators. If you can use Excel and email, you can use this portal. The [HR User Guide](HR_USER_GUIDE.md) explains everything in simple terms.

### Q: How long does it take to learn?
**A**: Most HR admins are comfortable with basic operations within 2-4 hours. Full mastery of all features typically takes 2-3 weeks of regular use. See the [Onboarding Checklist](HR_ADMIN_ONBOARDING.md).

### Q: Is training available?
**A**: Yes, we provide:
- Written guides ([HR User Guide](HR_USER_GUIDE.md))
- Step-by-step checklists
- Video tutorials (if available)
- On-demand support via GitHub issues

### Q: Can I test without affecting real data?
**A**: Yes! Create test employees with "TEST" in the name, experiment with features, then delete them. Never modify real employee data for testing.

---

## Account & Access

### Q: How do I log in for the first time?
**A**: 
1. Go to the portal URL provided by your IT team
2. Enter your employee ID
3. Open the secure one-time login link **or** enter the system-generated temporary password sent to you by your IT/HR team via a secure channel (email or SMS)
4. If you used a temporary password, you'll be prompted to change it immediately before continuing
5. Choose a strong, unique password that only you know, confirm it, and then log in

**Security Note**: Initial access is always via a system-generated one-time password or invitation link, never using personal data like date of birth. Do not reuse old passwords; set a strong, unique password that is not based on easily guessable information.

### Q: I forgot my password. What do I do?
**A**: Contact your system administrator or IT support. Password reset functionality may be available in the future, but currently requires admin intervention.

### Q: What's the difference between Admin and HR roles?
**A**: 
- **Admin**: Full access - can manage employees, compliance, system settings, and user roles
- **HR**: Can manage employees and compliance, but cannot change system settings or user roles
- **Viewer**: Read-only access - can view but not modify data

For solo operators, you typically have the **Admin** or **HR** role.

### Q: Can I access the portal from my phone?
**A**: Yes, the portal is responsive and works on mobile browsers. However, for complex tasks like bulk imports or generating reports, we recommend using a desktop/laptop.

### Q: Is there a mobile app?
**A**: Not currently. The web portal works on mobile browsers, which provides the same functionality.

### Q: Can multiple people use the portal at once?
**A**: Yes! The portal supports multiple concurrent users. Changes by one user are reflected for others in real-time (after refresh).

---

## Employee Management

### Q: How do I add a new employee?
**A**:
1. Go to the Employees section
2. Click "Add Employee" or "New Employee"
3. Fill in required fields (marked with *)
4. Save the basic information
5. Add personal details, compliance info, and documents separately
6. Verify all information is correct

**See detailed guide**: [HR User Guide - Adding Employees](HR_USER_GUIDE.md#adding-employees)

### Q: Can I import multiple employees at once?
**A**: Yes, using CSV import:
1. Download the CSV template from the portal
2. Fill in employee data following the template format
3. Upload the CSV file
4. Review any errors or warnings
5. Confirm the import

**Important**: Test with 2-3 employees first before bulk import.

### Q: What's the difference between employee layers?
**A**: The portal separates data into 3 layers:
1. **Employee Master**: Basic info (name, ID, department, job title)
2. **Personal Details**: Personal info (DOB, nationality, emergency contacts)
3. **Compliance Data**: UAE requirements (visa, EID, medical, contracts)

This separation ensures sensitive data is protected and clearly organized.

### Q: Can I edit employee information after adding them?
**A**: Yes, you can edit any employee information at any time. Changes are logged for audit purposes.

### Q: How do I deactivate an employee who left?
**A**: 
1. Go to the employee's profile
2. Change "Employment Status" to "Inactive" or "Terminated"
3. Update the "Last Working Day"
4. Keep the record for historical/compliance purposes
5. Do NOT delete the employee record

**Important**: Inactive employees don't count against compliance alerts but remain in the system for reporting.

### Q: Can I permanently delete an employee?
**A**: For data protection and audit purposes, employee records should be archived, not deleted. Contact your system administrator if deletion is absolutely necessary due to legal requirements.

---

## UAE Compliance

### Q: What compliance requirements does the portal track?
**A**: The portal tracks these UAE labor law requirements:
- **Visa**: Visa number, issue date, expiry date
- **Emirates ID**: EID number, expiry date
- **Medical Fitness**: Certificate issue date, expiry date
- **Insurance (ILOE)**: Status, expiry date
- **Employment Contracts**: Type, start date, end date
- **Probation Period**: Start, end (calculated automatically)

### Q: How do visa expiry alerts work?
**A**: The system automatically checks visa expiry dates and alerts you:
- **60 days before**: Initial warning
- **30 days before**: Urgent reminder
- **7 days before**: Critical alert

Alerts appear on the compliance dashboard. Email notifications may also be sent (if configured).

### Q: What's the difference between limited and unlimited contracts?
**A**:
- **Limited Contract**: Fixed end date, expires automatically, typical for specific projects
- **Unlimited Contract**: No fixed end date, continues until terminated by either party

The portal tracks both types and their specific requirements.

### Q: How does the system calculate probation periods?
**A**: Based on UAE labor law:
- Probation period is typically 6 months (180 days)
- Calculated from the contract start date
- Displayed in the employee profile
- Can be customized if different terms were agreed

### Q: What happens if I miss a visa renewal?
**A**: The system:
1. Continues to alert you (alerts don't stop)
2. Marks the visa as "Expired" after the expiry date
3. Flags the employee in compliance reports
4. May affect MOHRE reporting (if integrated)

**Action**: Update the visa information immediately after renewal.

### Q: Can the portal submit data directly to MOHRE?
**A**: Not currently. The portal generates reports in formats compatible with MOHRE requirements, but submission is manual. Direct integration may be added in future versions.

### Q: How do I prepare for a MOHRE inspection?
**A**:
1. Generate compliance report (all employees)
2. Verify all visa/EID/medical data is current
3. Check all contract dates are accurate
4. Ensure all documents are uploaded
5. Generate department summaries
6. Print or export required reports

The portal helps you stay audit-ready at all times.

### Q: Are compliance alerts sent automatically?
**A**: The portal generates alerts on the dashboard automatically. Email notifications depend on your system configuration. Check with your IT team about email alert setup.

---

## Documents & Files

### Q: What types of documents can I upload?
**A**: Common document types:
- Passport copies (PDF, JPG)
- Visa copies (PDF, JPG)
- Emirates ID copies (PDF, JPG)
- Medical fitness certificates (PDF)
- Employment contracts (PDF)
- Educational certificates (PDF)
- Other HR documents

**Recommended format**: PDF for official documents, JPG/PNG for ID card scans.

### Q: Is there a file size limit?
**A**: Typically 10-20 MB per file. If you need to upload larger files, compress them or split into multiple files.

### Q: Are documents encrypted?
**A**: Yes, documents are stored securely. Access is restricted based on user roles. Only authorized HR/Admin users can view sensitive documents.

### Q: Can employees view their own documents?
**A**: If employee self-service is enabled, employees can view their own documents. Configuration depends on your setup.

### Q: How do I organize documents?
**A**: Documents are automatically organized by:
- Employee (all docs for one employee together)
- Document type (passport, visa, EID, etc.)
- Upload date

Use clear, descriptive filenames when uploading.

### Q: Can I delete uploaded documents?
**A**: Yes, but be cautious:
- Old documents should be archived, not deleted
- Keep previous versions for audit trail
- Only delete if uploaded in error

**Best practice**: Upload new version rather than deleting old.

### Q: What if a document won't upload?
**A**: Troubleshooting steps:
1. Check file size (must be under limit)
2. Check file format (must be supported type)
3. Try a different browser
4. Check internet connection
5. Try compressing/converting the file
6. Contact support if issue persists

---

## Reports & Analytics

### Q: What reports are available?
**A**: Standard reports include:
- **Employee List**: All employees with key details
- **Compliance Summary**: Visa/EID/Medical expiry tracking
- **Department Breakdown**: Employees by department
- **Contract Expiry**: Upcoming contract end dates
- **Probation Report**: Employees in probation period

Custom reports may also be available depending on configuration.

### Q: Can I export reports to Excel?
**A**: Yes, most reports can be exported to:
- Excel (.xlsx)
- CSV (.csv)
- PDF (.pdf)

Use the export button on the report page.

### Q: How often should I generate compliance reports?
**A**: Recommended frequency:
- **Daily**: Check compliance dashboard (2 minutes)
- **Weekly**: Review upcoming expiries (15 minutes)
- **Monthly**: Full compliance audit (30 minutes)
- **Quarterly**: Deep analysis and planning (1-2 hours)

### Q: Can I schedule reports to run automatically?
**A**: This depends on your configuration. Check with your IT team. If not available, set calendar reminders to generate reports manually.

### Q: Reports are slow to generate. Why?
**A**: Possible reasons:
- Large amount of data
- Complex filters applied
- Server load
- Internet connection speed

**Solutions**: 
- Run reports during off-peak hours
- Use simpler filters
- Export smaller date ranges
- Contact support if consistently slow

### Q: Can I customize reports?
**A**: Basic customization is available (filters, date ranges, columns). Advanced custom reports may require technical support.

---

## Troubleshooting

### Q: The portal is loading slowly. What can I do?
**A**:
1. Check your internet connection
2. Try a different browser
3. Clear browser cache and cookies
4. Close unnecessary browser tabs
5. Check if other websites are also slow
6. Contact support if problem persists

### Q: I can't log in. What should I check?
**A**:
1. Verify you're using the correct URL
2. Check employee ID is correct (no spaces)
3. Check password is correct (case-sensitive)
4. Try resetting password
5. Try a different browser
6. Check with IT if account is active

### Q: Changes I made aren't showing. Why?
**A**:
1. Refresh the page (F5 or Cmd+R)
2. Check if changes were saved successfully
3. Look for error messages
4. Try logging out and back in
5. Clear browser cache
6. Check with other users if they see changes

### Q: I see an error message. What does it mean?
**A**: Common errors:
- **"Unauthorized"**: You don't have permission for this action
- **"Session expired"**: Log out and log back in
- **"Validation error"**: Check required fields are filled correctly
- **"Network error"**: Check internet connection

For other errors, note the exact message and contact support.

### Q: The portal is completely down. What do I do?
**A**:
1. Check if it's just you (ask colleague to try)
2. Try different device/network
3. Check GitHub for maintenance notifications
4. Contact IT/system administrator
5. Check deployment status (if you have access)

**Emergency**: If critical HR work is blocked, use temporary manual processes and sync data later.

### Q: Can I undo a change?
**A**: Direct undo is not available, but you can:
1. Edit the record back to previous state
2. Check change log to see what was changed
3. Contact support to restore from backup (extreme cases)

**Best practice**: Double-check before saving important changes.

---

## System Maintenance

### Q: Who maintains the portal?
**A**: 
- **Automated maintenance**: GitHub Copilot agents perform routine checks
- **Updates**: Applied via GitHub Actions workflows
- **Monitoring**: Automated health checks run after deployments
- **You**: Approve updates and test functionality

### Q: What is Dependabot and should I approve its PRs?
**A**: Dependabot automatically creates Pull Requests (PRs) to update software libraries. 

**Should you approve**:
- ✅ **Security updates**: Approve quickly (within 1-2 days)
- ✅ **Minor updates**: Approve after testing (within 1 week)
- ⚠️ **Major updates**: Test thoroughly before approving

**See**: [Copilot Agent System Guide](COPILOT_AGENT_SYSTEM_GUIDE.md) for details.

### Q: What are GitHub Actions and do I need to do anything?
**A**: GitHub Actions are automated tasks that:
- Run tests when code changes
- Check for security issues
- Deploy updates
- Monitor system health

**You don't need to manage them** - they run automatically. Just review the results and notifications.

### Q: When should I schedule maintenance?
**A**: Best times for UAE/Abu Dhabi:
- **Time**: Friday evening (6 PM) to Saturday morning
- **Duration**: 2-4 hours including testing
- **Frequency**: Monthly is ideal
- **Notice**: Inform users 48 hours in advance

### Q: How do I know if the system is healthy?
**A**: Check these indicators:
- ✅ Portal loads quickly (< 3 seconds)
- ✅ No error messages on dashboard
- ✅ Recent health check passed (see workflows)
- ✅ No critical alerts in GitHub issues
- ✅ All features working normally

**Monthly**: Review system health report (auto-generated).

### Q: What is a rollback and when do I need it?
**A**: A rollback returns the system to a previous working version.

**Need rollback when**:
- Major features broken after update
- Portal unusable
- Data integrity issues
- Critical security problem introduced

**See**: [Deployment Guide](GITHUB_DEPLOYMENT_OPTIONS.md) for rollback instructions.

### Q: How often should I backup data?
**A**: Backups should run automatically. Verify:
- **Frequency**: Daily or more
- **Storage**: Secure location
- **Testing**: Restore test quarterly

Check with IT team about backup configuration.

---

## Security & Privacy

### Q: Is employee data secure?
**A**: Yes, security measures include:
- Encrypted connections (HTTPS)
- Role-based access control
- Input sanitization (prevents injection attacks)
- Regular security scans
- Audit logs
- Secure document storage

### Q: Who can see employee data?
**A**: Access is role-based:
- **Admins/HR**: Full access to all data
- **Managers**: Access to their team's data only
- **Employees**: Access to their own data only (if self-service enabled)
- **Viewers**: Read-only access (if configured)

### Q: Are passwords stored securely?
**A**: Yes, passwords are:
- Hashed (not stored in plain text)
- Salted (protected against rainbow tables)
- Never visible to admins
- Never sent via email

### Q: What if I suspect unauthorized access?
**A**:
1. **Immediately**: Change your password
2. **Check**: Review audit logs for unusual activity
3. **Report**: Contact IT/security team urgently
4. **Document**: Note what you observed
5. **Monitor**: Watch for further suspicious activity

**Critical**: If employee data may be compromised, notify management immediately.

### Q: Can I share my login with colleagues?
**A**: **NO!** Never share login credentials. If a colleague needs access:
1. Request a separate account for them
2. Assign appropriate role/permissions
3. Each person should have their own account for audit purposes

### Q: How long is data retained?
**A**: Typically:
- **Active employees**: Indefinitely
- **Inactive employees**: 5-7 years (per UAE labor law)
- **Audit logs**: 1-3 years
- **Documents**: Per retention policy

Check your organization's data retention policy.

### Q: Is the portal GDPR compliant?
**A**: The portal includes features that support GDPR compliance (data encryption, access controls, audit logs), but GDPR compliance is an organizational responsibility. Consult with your legal team about specific requirements.

### Q: What happens to data if an employee requests deletion?
**A**: Under UAE law and data protection regulations, you may be required to delete personal data upon request. Contact legal counsel before permanently deleting employee records. The portal supports archiving as an alternative to deletion.

---

## Automated Reviews & Copilot

### Q: What is the Copilot Agent System?
**A**: An automated system that:
- Reviews code changes for quality
- Checks for security vulnerabilities
- Monitors deployments
- Suggests maintenance
- Provides plain-language explanations

**Think of it as**: Your technical assistant that works 24/7.

**See**: [Copilot Agent System Guide](COPILOT_AGENT_SYSTEM_GUIDE.md) for full details.

### Q: Do I need to understand the technical reviews?
**A**: No! The system provides **plain-language summaries** for non-technical users. Technical details are for developers.

**What you need to know**:
- 🟢 Green = Safe to proceed
- 🟡 Yellow = Caution, review recommended
- 🔴 Red = Stop, issues must be fixed

### Q: What is a Pull Request (PR)?
**A**: A Pull Request is a proposed change to the code. Think of it as a suggestion that needs approval before it goes live.

**Your role**:
1. Read the PR description (what's changing)
2. Review automated checks (are they passing?)
3. Check if UAE compliance is affected
4. Test if possible
5. Approve or request changes

### Q: How do I approve a Pull Request?
**A**:
1. Go to the PR on GitHub
2. Review the "Files changed" tab
3. Check that all automated checks passed (green checkmarks)
4. Click "Review changes" (top right)
5. Select "Approve"
6. Click "Submit review"
7. Click "Merge pull request"

**Only approve if**: All checks pass and you understand what's changing.

### Q: What if automated checks fail?
**A**: 
1. **Don't approve or merge**
2. **Read the error message** (look for plain-language explanation)
3. **Check if it's critical** (security issues = stop immediately)
4. **Request changes** if you opened the PR
5. **Contact the developer** if someone else opened it
6. **Wait for fixes** before re-reviewing

### Q: What are health checks and should I worry about them?
**A**: Health checks run automatically after deployments to ensure the portal still works.

**You should worry if**:
- ❌ Health check fails
- 🚨 Critical features broken
- 📧 You receive error notifications

**You can ignore if**:
- ✅ Health check passes
- 📊 Performance is normal
- 📝 Manual verification successful

### Q: I got a maintenance notification. What do I do?
**A**: Maintenance notifications fall into categories:

**Security (Red - Urgent)**:
- Review immediately
- Approve security updates within 24-48 hours
- Test after applying
- Don't delay

**Updates (Yellow - Important)**:
- Review within 1 week
- Schedule during maintenance window
- Test thoroughly

**Cleanup (Green - Optional)**:
- Review when convenient
- Good housekeeping, not critical
- Schedule during slow period

### Q: Can I disable automated reviews?
**A**: Not recommended, but you can:
- Ignore minor warnings (cosmetic issues)
- Configure notification frequency
- Delegate review to technical team

**Critical reviews** (security, compliance) should never be disabled.

---

## Still Have Questions?

### How to Get Help

**Documentation**:
1. [HR User Guide](HR_USER_GUIDE.md) - Detailed how-to guide
2. [Onboarding Checklist](HR_ADMIN_ONBOARDING.md) - Step-by-step learning
3. [Copilot Agent System Guide](COPILOT_AGENT_SYSTEM_GUIDE.md) - Maintenance and automation
4. [System Health Check](SYSTEM_HEALTH_CHECK.md) - System status

**Support Channels**:
- **GitHub Issues**: For bugs, feature requests, general questions
- **Email**: <!-- Add support email -->
- **Emergency**: <!-- Add emergency contact -->

**Creating a Good Support Request**:
1. **Title**: Clear and specific
2. **Description**: What you were trying to do
3. **Error**: Exact error message (if any)
4. **Steps**: How to reproduce the issue
5. **Impact**: How it affects your work
6. **Screenshots**: If UI-related

**Response Times**:
- Critical (portal down): < 2 hours
- High (feature broken): < 24 hours
- Medium (workaround exists): < 48 hours
- Low (question, suggestion): < 1 week

---

## Contributing to This FAQ

Found an answer that helped you? Have a question that's not here? Help other users by:

1. **Submit new questions**: Create a GitHub issue with title `[FAQ] Your Question`
2. **Improve answers**: Submit a PR with clearer explanations
3. **Add examples**: Real-world examples make answers better
4. **Translate**: Arabic translations welcome

---

**FAQ Version**: 1.0  
**Last Updated**: January 2026  
**Next Review**: After 50 user questions collected

---

**This FAQ is maintained by**: HR Portal users and contributors
**Repository**: https://github.com/ismaelloveexcel/HR-PORTAL-AZURE
