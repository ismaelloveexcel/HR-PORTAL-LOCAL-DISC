# 🚀 Immediate Deployment Guide

> **URGENT DEPLOYMENT** - Get your HR Portal running in under 5 minutes!

## 🏆 Option 1: Local Desktop (RECOMMENDED - Completely Hidden URL)

**Why Local Desktop?**
- ✅ **URL shows `localhost:5000`** - No external service visible
- ✅ **100% Private** - Data never leaves your computer
- ✅ **No third-party domains** - Users see only "localhost"
- ✅ **No subscription costs** - Completely free
- ✅ **Works offline** - Once installed

### Windows (One-Click)
```batch
scripts\one-click-deploy-windows.bat
```

### macOS/Linux (One-Click)
```bash
chmod +x scripts/one-click-deploy.sh
./scripts/one-click-deploy.sh
```

Access at: **http://localhost:5000**

Users will only see `localhost` in the URL - no indication of external hosting.

---

## Option 2: GitHub Codespaces (Quick Cloud Setup)

**Note:** Codespaces URLs contain `github.dev` in them. If you need a completely hidden URL, use Local Desktop above.

**Why Codespaces?**
- ✅ **No local setup required** - Everything runs in the cloud
- ✅ **Private URLs** - Only accessible when logged into GitHub
- ✅ **Free tier** - 60 hours/month included
- ⚠️ **URL contains github.dev** - Not completely hidden

### Quick Start (2 Minutes)

1. **Click the green "Code" button** on the repository
2. **Click "Codespaces" tab**
3. **Click "Create codespace on main"**
4. **Wait 2-3 minutes** for automatic setup
5. **Done!** Your HR Portal is running

### Access Your Portal

After setup completes:
1. Click the **PORTS** tab at the bottom of VS Code
2. Click the **globe icon** next to port **5000**
3. Your URL opens (format: `xxxx-5000.app.github.dev`)

---

## Default Login Credentials

| Employee ID | Role | Password |
|-------------|------|----------|
| BAYN00008 | Admin | Date of birth (DDMMYYYY) |

**First login**: Use your date of birth as password, then create a new secure password.

---

## URL Comparison

| Option | URL Shown to Users | External Service Visible? |
|--------|-------------------|---------------------------|
| **Local Desktop** | `http://localhost:5000` | ❌ No |
| **Tailscale + Local** | `http://100.x.x.x:5000` | ❌ No |
| **GitHub Codespaces** | `xxx.app.github.dev` | ✅ Yes ("github" visible) |
| **Azure + Custom Domain** | `yourcompany.com` | ❌ No (requires domain) |

**For completely hidden URLs**, use **Local Desktop** deployment.

---

## Troubleshooting

### Local Desktop Issues

**Backend not starting?**
```bash
cd backend
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Frontend not loading?**
```bash
cd frontend
npm run dev
```

### Codespaces Issues

**Can't access the portal?**
- Ensure you're logged into GitHub
- Check PORTS tab for the correct URL

**Backend logs:**
```bash
cat /tmp/backend.log
```

---

## Support

Need help? Check:
- [HR User Guide](docs/HR_USER_GUIDE.md)
- [Deployment Options](docs/GITHUB_DEPLOYMENT_OPTIONS.md)
