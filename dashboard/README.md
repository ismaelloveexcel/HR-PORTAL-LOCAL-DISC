# Repository Dashboard

A simple, visual dashboard to help you monitor and control your GitHub repository.

## What is This?

This is a **repository control panel** that helps you:
- ✅ Monitor workflow statuses at a glance
- ✅ Quickly access Actions, PRs, Issues, and Settings
- ✅ Discover useful GitHub features you might not know about
- ✅ Understand common errors and how to fix them
- ✅ Get quick links to all your workflows

## Why Use This Dashboard?

With 26+ workflows in this repository, it can be overwhelming to keep track of everything. This dashboard simplifies it by:

1. **Centralizing Links**: All important links in one place
2. **Visual Status**: See which workflows are passing/failing
3. **Quick Actions**: One-click access to common tasks
4. **Learning Aid**: Discover GitHub features like Insights, Pulse, Network graphs
5. **Troubleshooting Guide**: Step-by-step help for common issues

## How to Use

### Option 1: View Locally
```bash
# Open in browser
open dashboard/index.html

# Or use a simple HTTP server
cd dashboard
python3 -m http.server 8080
# Visit http://localhost:8080
```

### Option 2: Deploy to GitHub Pages

1. **Enable GitHub Pages**:
   - Go to: Repository → Settings → Pages
   - Source: Select "GitHub Actions"
   - Save

2. **Deploy**: Push to main branch or manually trigger workflow

3. **Access**: `https://ismaelloveexcel.github.io/AZURE-DEPLOYMENT-HR-PORTAL/`

## What's Included

### 📊 Repository Stats
- Total workflows count
- File counts
- Deployment platform info

### ⚡ Quick Actions
- Direct links to Actions, PRs, Issues, Settings
- One-click navigation

### 🔄 Key Workflows
- Status indicators for main workflows
- Direct links to each workflow's runs
- Visual status dots (green = passing, yellow = warning)

### ✨ GitHub Features
- **Actions Tab**: See all workflow runs, re-run failed jobs
- **Insights → Pulse**: Activity overview
- **Insights → Network**: Branch/commit visualization
- **Security Tab**: Dependabot alerts, code scanning

### 🔧 Troubleshooting
- Step-by-step guides for common issues:
  - Workflow failures
  - Deployment errors
  - Build errors

### 🔔 Stay Updated
- Configure repository notifications
- Email notification settings

## Features

- **Simple HTML/CSS**: No build process, no dependencies
- **Responsive**: Works on desktop, tablet, and mobile
- **Fast**: Lightweight, loads instantly
- **Bookmarkable**: Bookmark for quick access

## Customization

Edit `dashboard/index.html` to:
- Update repository links
- Add/remove workflow cards
- Modify status indicators
- Change styling

Edit `dashboard/styles.css` to:
- Adjust colors
- Modify layout
- Change fonts

## Deployment

The dashboard deploys automatically via `.github/workflows/github-pages.yml` when:
- Changes pushed to `/dashboard` directory
- Workflow manually triggered

## Benefits Over GitHub UI

1. **All-in-One View**: See everything important on one page
2. **Faster Navigation**: Direct links without menu navigation
3. **Learning Tool**: Discover GitHub features with descriptions
4. **Customizable**: Tailor to your workflow
5. **Always Available**: Works offline if opened locally

## Pro Tips

- **Bookmark it**: Add to browser favorites for instant access
- **Pin workflows**: Right-click workflow links → bookmark for quick re-runs
- **Check regularly**: Use as your "repo health check" homepage
- **Share with team**: Give team members easy access to monitoring

## Next Steps

1. Deploy dashboard to GitHub Pages (see instructions above)
2. Bookmark the dashboard URL
3. Check it daily for workflow status
4. Explore the GitHub features linked in the dashboard

## See Also

- Main application: `/frontend` and `/backend`
- Deployment guide: `/docs/AZURE_DEPLOYMENT_REFERENCE_GUIDE.md`
- GitHub Actions: `.github/workflows/`
