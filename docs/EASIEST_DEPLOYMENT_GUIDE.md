# Easiest Deployment Guide for HR Portal

> 🎯 **Your Goal:** Deploy HR Portal quickly without third-party URLs visible outside Microsoft ecosystem

---

## 🚀 ONE-CLICK DEPLOYMENT (EASIEST!)

**Just double-click and wait - everything installs automatically!**

### Windows Users:
1. Download this project: Click green "Code" button → "Download ZIP" on GitHub
2. Extract the ZIP file to your Desktop
3. Open the extracted folder
4. Go into the `scripts` folder
5. **Double-click `one-click-deploy-windows.bat`**
6. Wait 5-10 minutes (it installs Python, Node.js, and everything else)
7. Your browser will open automatically with the HR Portal!

### Mac Users:
1. Open Terminal (press Cmd+Space and type "Terminal")
2. Download the project:
```bash
git clone https://github.com/ismaelloveexcel/HR-PORTAL-AZURE.git
```
3. Navigate to the folder:
```bash
cd HR-PORTAL-AZURE
```
4. Run the one-click installer:
```bash
chmod +x scripts/one-click-deploy.sh
./scripts/one-click-deploy.sh
```
5. Wait 5-10 minutes
6. Your browser will open automatically!

**That's it! No manual installation needed.**

---

## 🆘 MANUAL INSTALLATION (If One-Click Doesn't Work)

**If you've never done this before, follow these exact steps:**

### Step 1: Download and Install Python (5 minutes)

1. Open your web browser
2. Go to: **https://www.python.org/downloads/**
3. Click the big yellow **"Download Python 3.xx"** button
4. Run the downloaded file
5. ⚠️ **IMPORTANT**: Check the box that says **"Add Python to PATH"** before clicking Install
6. Click **Install Now** and wait for it to finish

### Step 2: Download and Install Node.js (5 minutes)

1. Go to: **https://nodejs.org/**
2. Click the **LTS** button (the one that says "Recommended For Most Users")
3. Run the downloaded file
4. Click **Next** through all the screens and **Install**
5. Wait for it to finish

### Step 3: Download This Project (2 minutes)

1. Go to: **https://github.com/ismaelloveexcel/HR-PORTAL-AZURE**
2. Click the green **Code** button
3. Click **Download ZIP**
4. Find the downloaded ZIP file in your Downloads folder
5. Right-click and select **Extract All** (Windows) or double-click (Mac)
6. Move the extracted folder somewhere easy to find (like Desktop)

### Step 4: Run the Installer (5 minutes)

**On Windows:**
1. Open the extracted folder
2. Go into the `scripts` folder
3. Double-click on `install-windows.bat`
4. A black window will open - let it run (takes about 3-5 minutes)
5. When it asks questions, type `Y` and press Enter

**On Mac:**
1. Open **Terminal** (search for "Terminal" in Spotlight)
2. Type: `cd ` (with a space after cd)
3. Drag the extracted folder into the Terminal window
4. Press Enter
5. Type: `chmod +x scripts/install.sh && ./scripts/install.sh`
6. Press Enter and follow the prompts

### Step 5: Start the App (30 seconds)

**On Windows:**
1. Double-click `scripts\start-portal-windows.bat`

**On Mac:**
1. In Terminal, type: `./scripts/start-portal.sh`

### Step 6: Open in Browser

1. Open your web browser (Chrome, Edge, Safari, etc.)
2. Go to: **http://localhost:5000**
3. 🎉 **You should see the HR Portal!**

### If Something Goes Wrong:

- **"Python not found"** → Go back to Step 1, make sure you checked "Add to PATH"
- **"Node not found"** → Go back to Step 2, reinstall Node.js
- **Black window closes immediately** → Right-click the .bat file, select "Run as administrator"
- **Still stuck?** → Take a screenshot of the error and share it

---

## 📋 Quick Assessment

Based on your requirements:
- ❌ No Replit (hidden costs, obvious domain)
- ❌ No Vercel/Netlify (non-Microsoft domains)
- ❌ Azure is too complex
- ✅ Need something within Microsoft ecosystem or hidden

---

## 🏆 RECOMMENDED: Local Desktop Deployment (EASIEST - 10 minutes)

**This is the fastest path to a working HR Portal with complete privacy.**

### Why This is Best for You:
- ✅ **100% Free** - No costs ever
- ✅ **100% Private** - Data stays on your computer
- ✅ **No third-party domains** - Runs on localhost
- ✅ **No Azure complexity** - No cloud setup needed
- ✅ **Works offline** - Once installed
- ✅ **Uses SQLite** - No PostgreSQL setup needed

### Prerequisites (5 minutes one-time)

1. **Python 3.11+** - [Download here](https://www.python.org/downloads/)
2. **Node.js 20+** - [Download here](https://nodejs.org/) (required for React Router v7)

### Installation (5 minutes)

**macOS/Linux:**
```bash
# Navigate to project directory
cd /path/to/HR-PORTAL-AZURE

# Run the installer
chmod +x scripts/install.sh
./scripts/install.sh
```

**Windows:**
```batch
# Navigate to project directory
cd \path\to\HR-PORTAL-AZURE

# Run the installer
scripts\install-windows.bat
```

### Starting the App (30 seconds)

**macOS/Linux:**
```bash
./scripts/start-portal.sh
```

**Windows:**
```batch
scripts\start-portal-windows.bat
```

### Access URLs (Local Only)
- **Application:** http://localhost:5000
- **API Documentation:** http://localhost:8000/docs

---

## 🔄 Option 2: GitHub Codespaces (Cloud but Microsoft Domain)

**If you need cloud access but want Microsoft infrastructure:**

### Advantages:
- ✅ Runs on github.dev (Microsoft-owned)
- ✅ Private URLs (not publicly indexed)
- ✅ 60 hours/month FREE
- ✅ No laptop required
- ✅ Pre-configured development environment

### Setup (5 minutes):

1. Go to your repository on GitHub
2. Click **Code** → **Codespaces** → **Create codespace on main**
3. Wait 2-3 minutes for environment to start
4. In the terminal, run:

```bash
# Setup backend
cd backend
pip install uv
uv sync
cp .env.example .env

# Run migrations (will use SQLite for simplicity)
uv run alembic upgrade head

# Start backend (Terminal 1)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

5. Open a new terminal (Ctrl+Shift+\`) and run:

```bash
# Start frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

6. Click on **Ports** tab at bottom, find port 5000, click the URL

### Privacy:
- Set ports to **Private** to prevent public access
- URLs look like: `https://xxx-5000.app.github.dev`
- Not publicly discoverable

---

## 💡 Simpler Alternative: SQLite Instead of PostgreSQL

The main complexity in deployment comes from PostgreSQL. Here's how to use SQLite (file-based database) instead:

### One-Time Configuration:

Edit `backend/.env` to use SQLite:

```bash
# Change this line:
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# To this (SQLite format - the app will automatically convert it):
DATABASE_URL=sqlite:///./hr_portal.db
```

**Note:** The app automatically converts `sqlite://` to `sqlite+aiosqlite://` for async support.

**Benefits:**
- ✅ No database server to manage
- ✅ Single file backup (`hr_portal.db`)
- ✅ Works everywhere

**Limitation:**
- Not recommended for multi-user concurrent access (fine for solo HR user)

---

## 🔍 Pass Generation Alternatives

If your **primary need is just pass generation**, consider these simpler alternatives:

### 1. Microsoft Lists + Power Automate (No Code)

If you just need to track visitors/passes:
- Create a Microsoft List for passes
- Use Power Automate to generate pass numbers
- Print directly from SharePoint

**Pros:** Fully in Microsoft 365, no coding
**Cons:** Less flexible, no QR codes

### 2. QR Code Badge Templates (Excel/Word)

For simple pass generation:
- Excel with pass data
- Word Mail Merge template
- Free QR code generator

### 3. Power Apps (Low Code, Microsoft)

Build a simple pass tracker with:
- Power Apps for the interface
- SharePoint list for storage
- Power Automate for workflows

**Cost:** Included in Microsoft 365 Business

---

## 📊 Comparison Summary

| Option | Setup Time | Cost | Privacy | Complexity |
|--------|-----------|------|---------|------------|
| **Local Desktop** | 10 min | Free | ⭐⭐⭐⭐⭐ | Easy |
| **GitHub Codespaces** | 5 min | Free (60h/mo) | ⭐⭐⭐⭐ | Easy |
| **Azure App Service** | 2-3 hours | $15-50/mo | ⭐⭐⭐⭐ | Hard |
| **Microsoft 365 + Power Apps** | 1-2 hours | Included | ⭐⭐⭐⭐⭐ | Medium |

---

## 🚀 Quick Decision Guide

### Choose **Local Desktop** if:
- You're the only user
- Data privacy is critical
- You want zero ongoing costs
- You have Python/Node.js installed

### Choose **GitHub Codespaces** if:
- You need access from multiple devices
- You don't want to install anything locally
- 60 hours/month is sufficient
- You want Microsoft infrastructure

### Choose **Power Apps** if:
- You just need basic pass tracking
- You have Microsoft 365 Business
- You prefer no-code solutions
- Integration with Teams/SharePoint matters

---

## 🛠️ Troubleshooting Local Installation

### "Python not found"
Download from: https://www.python.org/downloads/
Make sure to check "Add to PATH" during installation

### "Node.js not found"
Download from: https://nodejs.org/
Install the LTS version

### "uv not found"
```bash
pip install uv
# or
pip3 install uv
```

### "Port already in use"
Change the port in the start command:
```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8001  # Different port
```

### Database migration errors
If using SQLite, delete the old database and re-run:
```bash
rm backend/hr_portal.db
cd backend && uv run alembic upgrade head
```

---

## 📞 Need More Help?

If you're still having issues:

1. **Check prerequisites:** Python 3.11+, Node.js 20+
2. **Read the logs:** Error messages tell you what's wrong
3. **Try a fresh clone:** Sometimes starting fresh helps
4. **Use Codespaces:** If local setup fails, Codespaces works out of the box

---

## 🎉 Summary

**Fastest Path to Success:**

1. Install Python 3.11+ and Node.js 20+
2. Run `./scripts/install.sh` (or `scripts\install-windows.bat`)
3. Run `./scripts/start-portal.sh` (or `scripts\start-portal-windows.bat`)
4. Open http://localhost:5000

**Total time: 10-15 minutes**

---

<p align="center">
  <strong>Secure Renewals HR Portal</strong><br>
  Built with ❤️ for HR teams
</p>
