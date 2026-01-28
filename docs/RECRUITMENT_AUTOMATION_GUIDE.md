# Recruitment Automation Guide for Solo HR

## Overview
This guide shows you how to leverage automation to manage recruitment efficiently as a solo HR professional.

---

## 🤖 Daily Automation Tasks

### What Gets Automated
The system can automatically:
1. ✅ Send interview reminders (24 hours before)
2. ✅ Alert candidates on expiring offers (3 days before)
3. ✅ Mark expired offers as "Expired"
4. ✅ Update pipeline metrics
5. ✅ Track candidate activity

### How to Run (3 Options)

#### Option 1: Manual Trigger (Recommended to Start)
**When to use**: Daily, first thing in the morning

1. Log into the HR portal
2. Navigate to **Recruitment** → **Automation**
3. Click **"Run Daily Tasks"**
4. View results:
   ```
   ✅ Interview Reminders: 5 sent
   ✅ Offer Alerts: 2 sent
   ✅ Expired Offers: 1 marked
   ```

**Time**: 30 seconds

---

#### Option 2: API Call (Advanced)
**When to use**: Integrate with other tools

```bash
# Set your credentials
export API_URL="https://your-app.azurewebsites.net"
export ADMIN_TOKEN="your-jwt-token"

# Run all daily tasks
curl -X POST "$API_URL/api/recruitment/automation/run-all-daily-tasks" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

**Response**:
```json
{
  "success": true,
  "results": {
    "interview_reminders_sent": 5,
    "offer_alerts_sent": 2,
    "offers_marked_expired": 1
  },
  "message": "Daily automation completed: 5 reminders, 2 alerts, 1 expired offers"
}
```

---

#### Option 3: GitHub Actions (Fully Automated)
**When to use**: Set it and forget it

A workflow has been created at `.github/workflows/daily-recruitment-automation.yml`

**Setup Steps**:

1. **Configure Secrets** (One-time setup)
   ```
   Go to: GitHub → Settings → Secrets and variables → Actions
   
   Add:
   - AZURE_APP_URL: https://your-app.azurewebsites.net
   - ADMIN_PASSWORD: your-admin-password
   ```

2. **Test Manual Run**
   ```
   Go to: GitHub → Actions → Daily Recruitment Automation
   Click: "Run workflow"
   Wait: ~30 seconds
   Check: Green checkmark ✅
   ```

3. **Verify Automatic Runs**
   - Workflow runs automatically every day at 6:00 AM UTC
   - Check under **Actions** tab to see history
   - Adjust schedule in workflow file if needed

**Benefits**:
- ✅ Never forget to run automation
- ✅ Runs even when you're on leave
- ✅ Email notifications on failure
- ✅ Audit trail of all runs

---

## 📊 Individual Automation Endpoints

### Send Interview Reminders Only
```bash
POST /api/recruitment/automation/send-interview-reminders?hours_before=24
```

**Use Case**: Before a busy interview day

**Parameters**:
- `hours_before`: How many hours before interview to send (default: 24)

**Example**:
```bash
# Send reminders for interviews in next 48 hours
curl -X POST "$API_URL/api/recruitment/automation/send-interview-reminders?hours_before=48" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

### Send Offer Expiry Alerts Only
```bash
POST /api/recruitment/automation/send-offer-expiry-alerts?days_before=3
```

**Use Case**: Weekly check on pending offers

**Parameters**:
- `days_before`: Days before expiry to alert (default: 3)

**Example**:
```bash
# Alert on offers expiring in next 7 days
curl -X POST "$API_URL/api/recruitment/automation/send-offer-expiry-alerts?days_before=7" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

### Mark Expired Offers
```bash
POST /api/recruitment/automation/mark-expired-offers
```

**Use Case**: Clean up old offers

**Example**:
```bash
curl -X POST "$API_URL/api/recruitment/automation/mark-expired-offers" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## 🔔 Email Notifications

### Interview Reminders
**Sent to**: Candidates  
**When**: 24 hours before interview  
**Contains**:
- Position title
- Interview date & time
- Location or meeting link
- Interview type
- Duration
- Preparation tips

**Example Email**:
```
Subject: Interview Reminder: Senior Software Engineer

Dear John Doe,

This is a friendly reminder about your upcoming interview:

Position: Senior Software Engineer
Department: Engineering
Date: Thursday, January 25, 2026
Time: 10:00 AM
Duration: 60 minutes
Location: Video Call
Meeting Link: https://meet.company.com/abc123

Interview Type: Technical Interview

Please ensure you:
- Join on time
- Have a stable internet connection
- Prepare questions for the interviewer

We look forward to meeting you!

Best regards,
HR Team
```

---

### Offer Expiry Alerts
**Sent to**: Candidates  
**When**: 3 days before offer expires  
**Contains**:
- Offer number
- Position details
- Expiry date & time
- Action required

**Example Email**:
```
Subject: Action Required: Job Offer Expires in 3 Days

Dear Jane Smith,

⚠️ Your job offer will expire in 3 days.

Position: Marketing Manager
Department: Marketing
Offer Number: OFR-20260121-0001
Expires: January 24, 2026 at 11:59 PM

Please review and respond to the offer before it expires.

To accept or decline, log into your candidate portal or contact HR.

Best regards,
HR Team
```

---

## 📅 Recommended Automation Schedule

### Daily Tasks (Automated)
| Time | Task | Why |
|------|------|-----|
| 6:00 AM | Run all daily tasks | Before office hours |
| 8:00 AM | Review automation results | Start of day check |

### Weekly Tasks (Manual)
| Day | Task | Why |
|-----|------|-----|
| Monday | Review recruitment pipeline | Week planning |
| Wednesday | Check offer status | Mid-week follow-up |
| Friday | Export weekly metrics | Week closure |

### Monthly Tasks (Manual)
| Task | Why |
|------|-----|
| Review source effectiveness | Optimize job postings |
| Analyze time-to-fill | Process improvement |
| Clean up stale candidates | Database hygiene |

---

## 🔧 Troubleshooting Automation

### "No Reminders Sent"
**Possible Causes**:
- No interviews scheduled in the time window
- Candidates don't have email addresses
- SMTP not configured

**Fix**:
1. Check interview schedule
2. Verify candidate emails
3. Check SMTP settings in backend `.env`:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@company.com
   SMTP_PASSWORD=your-app-password
   SMTP_FROM_EMAIL=noreply@company.com
   SMTP_FROM_NAME=HR Portal
   SMTP_USE_TLS=true
   ```

---

### "Workflow Failed"
**Possible Causes**:
- Secrets not configured
- Backend not responding
- Authentication failed

**Fix**:
1. Check GitHub Secrets are set correctly
2. Verify backend is running: `curl https://your-app.azurewebsites.net/api/health`
3. Test authentication manually
4. Check workflow logs in GitHub Actions

---

### "Emails Not Received"
**Possible Causes**:
- Emails in spam folder
- SMTP credentials incorrect
- Email service blocked

**Fix**:
1. Check candidate's spam folder
2. Verify SMTP credentials
3. Test email service:
   ```bash
   # Backend logs should show "Email sent successfully"
   az webapp log tail --name your-app --resource-group your-rg
   ```
4. Use a dedicated email service (SendGrid, Mailgun, AWS SES)

---

## 📈 Monitoring Automation

### Key Metrics to Track
1. **Automation Run Success Rate**: Should be 100%
2. **Interview Reminder Delivery Rate**: Should be 100%
3. **Offer Response Rate**: Should improve after alerts
4. **Time-to-Hire**: Should decrease with automation

### Where to Check
- **GitHub Actions**: Go to Actions tab, see workflow history
- **Backend Logs**: `az webapp log tail` or check Azure Portal
- **Recruitment Metrics**: Dashboard → Analytics

---

## 💡 Pro Tips for Solo HR

### 1. Bookmark the Automation Dashboard
Create a browser bookmark for quick access:
```
https://your-app.azurewebsites.net/recruitment/automation
```

### 2. Set Up Mobile Notifications
Configure GitHub Actions to send Slack/Teams notifications on automation failures.

### 3. Create a Morning Checklist
```
[ ] Run daily automation (automated if using GitHub Actions)
[ ] Check automation results
[ ] Review new candidates
[ ] Respond to candidate queries
[ ] Schedule interviews
[ ] Update requisition status
```

### 4. Use Bulk Operations
Instead of moving candidates one-by-one:
- Select multiple candidates
- Click "Bulk Action"
- Choose "Move to Screening"
- Saves 80% of time!

### 5. Prepare Email Templates
System sends automated emails, but keep templates ready for:
- Rejection emails
- Custom follow-ups
- Special requests

---

## 🚀 Advanced Automation (Future)

### Coming Soon
- [ ] Candidate auto-ranking based on CV scores
- [ ] Auto-rejection of unqualified candidates
- [ ] Integration with calendar (Google/Outlook)
- [ ] WhatsApp notifications
- [ ] AI-powered candidate matching
- [ ] Auto-generated interview questions
- [ ] Reference check automation

### Request a Feature
Email: hr-tech@company.com  
Subject: "Recruitment Automation Feature Request"

---

## 📞 Support

**For Automation Issues**:
- Check troubleshooting section above
- Review workflow logs in GitHub Actions
- Contact IT if SMTP/Azure issues

**For Feature Requests**:
- Document your use case
- Estimate time savings
- Submit via HR portal

**Emergency Contact**:
- Email: hr-support@company.com
- Phone: +971-XX-XXX-XXXX

---

## 📚 Related Documentation

- [CEO Quick Start Guide](RECRUITMENT_CEO_GUIDE.md)
- [Recruitment Feature Technical Docs](../backend/app/routers/recruitment.py)
- [Email Service Configuration](../backend/app/services/email_service.py)
- [GitHub Actions Workflow](.github/workflows/daily-recruitment-automation.yml)

---

**Last Updated**: 2026-01-21  
**Version**: 2.0 (Automation Enhanced)  
**Maintainer**: HR Tech Team
