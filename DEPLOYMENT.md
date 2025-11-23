# 🚀 Streamlit Cloud Deployment Guide

Complete step-by-step guide to deploy the Stock Pattern Scanner on Streamlit Cloud (free tier).

## Prerequisites

- [x] GitHub account
- [x] Streamlit Cloud account (free)
- [x] Gmail account with app password
- [x] All project files ready

## Step 1: Prepare GitHub Repository

### 1.1 Create GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click **"New repository"**
3. Repository name: `stock-pattern-scanner`
4. Description: "Automated stock pattern detection with email alerts"
5. Choose **Public** (required for Streamlit Cloud free tier)
6. ✅ Initialize with README (optional - we have our own)
7. Click **"Create repository"**

### 1.2 Upload Project Files

**Method 1: GitHub Web Interface**

1. Click **"Add file"** → **"Upload files"**
2. Drag and drop all project files:
   ```
   ✅ app.py
   ✅ pattern_detector.py
   ✅ email_alerts.py
   ✅ market_utils.py
   ✅ data_manager.py
   ✅ requirements.txt
   ✅ README.md
   ✅ .gitignore
   ✅ sample_stocks.txt
   ```
3. Create `.streamlit` folder:
   - Click **"Add file"** → **"Create new file"**
   - Name: `.streamlit/config.toml`
   - Paste config.toml contents
   - Commit

**Method 2: Git Command Line**

```bash
# Initialize local git repository
git init
git add .
git commit -m "Initial commit: Stock pattern scanner"

# Connect to GitHub
git remote add origin https://github.com/YOUR-USERNAME/stock-pattern-scanner.git
git branch -M main
git push -u origin main
```

### 1.3 Verify Files

Check your repository has:
- ✅ All Python files (app.py, pattern_detector.py, etc.)
- ✅ requirements.txt
- ✅ .streamlit/config.toml
- ✅ README.md
- ✅ .gitignore
- ❌ NO secrets.toml (should be gitignored)

## Step 2: Create Gmail App Password

### 2.1 Enable 2-Factor Authentication

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Navigate to **Security**
3. Enable **2-Step Verification** if not already enabled

### 2.2 Generate App Password

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Select app: **"Mail"**
3. Select device: **"Other"** (enter "Stock Scanner")
4. Click **"Generate"**
5. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)
6. **Save it securely** - you'll need it in Step 3

## Step 3: Deploy to Streamlit Cloud

### 3.1 Sign Up / Sign In

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign in"**
3. Choose **"Continue with GitHub"**
4. Authorize Streamlit to access your repositories

### 3.2 Create New App

1. Click **"New app"** button
2. Fill in deployment settings:

   **Repository**:
   - Repository: `YOUR-USERNAME/stock-pattern-scanner`
   - Branch: `main`
   - Main file path: `app.py`

   **App URL** (optional):
   - Custom subdomain: `stock-scanner` (or your choice)
   - Full URL will be: `stock-scanner.streamlit.app`

3. Click **"Advanced settings..."**

### 3.3 Configure Secrets

In the **Secrets** section, paste:

```toml
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "abcd efgh ijkl mnop"
RECIPIENT_EMAIL = "recipient-email@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
```

**Replace**:
- `your-email@gmail.com` → Your Gmail address
- `abcd efgh ijkl mnop` → Your 16-char app password from Step 2
- `recipient-email@gmail.com` → Email where you want to receive alerts

### 3.4 Set Python Version (Optional)

In Advanced settings:
- Python version: `3.9` or `3.10`

### 3.5 Deploy!

1. Click **"Deploy!"**
2. Wait 2-5 minutes for deployment
3. Watch the logs for any errors

## Step 4: Configure the App

### 4.1 First Launch

1. Once deployed, your app will open automatically
2. You'll see the Stock Pattern Scanner interface

### 4.2 Configure Email

1. In sidebar, expand **"📧 Email Settings"**
2. Fields should auto-fill from secrets
3. Click **"Save Email Config"**
4. Look for ✅ success message

### 4.3 Load Stock List

**Option A: Paste Directly**
1. In sidebar, expand **"📊 Stock List"**
2. Paste stock symbols (one per line):
   ```
   RELIANCE
   TCS
   INFY
   HDFCBANK
   ICICIBANK
   ```
3. Click **"Load Stocks"**

**Option B: Use Sample File**
1. Copy contents from `sample_stocks.txt`
2. Paste in Stock List text area
3. Click **"Load Stocks"**

### 4.4 Start Scanner

1. Verify:
   - ✅ Email configured
   - ✅ Stocks loaded
   - ✅ Market status shows correctly

2. Click **"▶️ Start"** button

3. Check status:
   - Should show 🟢 **Active**
   - Last scan time will update
   - Scan count will increment

## Step 5: Verify Operation

### 5.1 Check Logs

In Streamlit Cloud dashboard:
1. Click **"Manage app"**
2. View **"Logs"** tab
3. Look for:
   ```
   INFO - Scheduler started successfully
   INFO - Starting TIER1 scan at 2024-...
   INFO - Fetched 252 rows for RELIANCE.NS
   ```

### 5.2 Test Email Alerts

**Method 1: Wait for real patterns**
- Scanner will email when patterns are detected
- May take hours/days depending on market

**Method 2: Manual test** (optional)
- Create a test pattern detection
- Check email inbox for alert
- Verify HTML formatting looks good

### 5.3 Monitor Active Patterns

1. Go to **"Active Patterns"** tab
2. Should populate as patterns are detected
3. Filter and sort to explore

### 5.4 Check Statistics

1. Go to **"Statistics"** tab
2. Monitor:
   - Total patterns detected
   - Confirmed breakouts
   - Pattern distribution

## Troubleshooting

### ❌ Deployment Failed

**Error: "No module named 'xyz'"**
- Fix: Add missing module to `requirements.txt`
- Redeploy app

**Error: "secrets.toml not found"**
- Fix: Add secrets in Streamlit Cloud dashboard
- App Settings → Secrets → Paste TOML

### ❌ Email Not Sending

**Check:**
1. Gmail app password is correct (16 chars, no spaces)
2. 2FA is enabled on Gmail
3. SMTP settings: `smtp.gmail.com:587`
4. Check app logs for email errors

**Fix:**
1. Regenerate Gmail app password
2. Update secrets in Streamlit Cloud
3. Restart app

### ❌ No Patterns Detected

**Reasons:**
1. Market is closed (scanner pauses automatically)
2. Stocks not forming patterns currently (normal)
3. Pattern criteria very strict (by design)

**Check:**
1. Market hours: Mon-Fri, 9:15 AM - 3:30 PM IST
2. Scanner status: Should be 🟢 Active
3. Logs: Should show "Starting TIER1 scan"

### ❌ App Crashes / Out of Memory

**Free Tier Limits:**
- 1 GB RAM
- 1 CPU core

**Solutions:**
1. Reduce stock list (try 100-200 stocks max)
2. Increase scan intervals
3. Optimize caching
4. Consider upgrading to paid tier

## Optimization Tips

### For Free Tier (1 GB RAM)

1. **Limit stock list**: 100-300 stocks maximum
2. **Reduce scan frequency**:
   ```python
   # In app.py, modify scan times
   scheduler.add_job(
       lambda: perform_scan('TIER1'),
       CronTrigger(day_of_week='mon-fri', hour='10,13,15', minute='0'),
       id='tier1_scan'
   )
   ```
3. **Disable less critical tiers**: Comment out TIER2/TIER4

### Data Caching

Already implemented:
- 5-minute cache for stock data
- Pattern deduplication
- Database cleanup (30 days)

## Monitoring & Maintenance

### Daily Checks

1. **Email alerts**: Verify alerts are arriving
2. **App status**: Check if app is running
3. **Logs**: Review for errors

### Weekly Maintenance

1. **Review statistics**: Check success rate
2. **Update stock list**: Add/remove stocks
3. **Clear old patterns**: Automatic (30 days)

### Monthly Review

1. **Pattern performance**: Analyze hit rate
2. **Adjust parameters**: Fine-tune if needed
3. **Update dependencies**: Check for security updates

## Updating the App

### Code Changes

1. **Edit files locally**
2. **Commit to GitHub**:
   ```bash
   git add .
   git commit -m "Update pattern detection logic"
   git push
   ```
3. **Streamlit auto-deploys**: Changes live in ~2 minutes

### Update Secrets

1. Streamlit Cloud dashboard
2. App Settings → Secrets
3. Edit TOML, save
4. Restart app

## Upgrading to Paid Tier

If you need more resources:

**Streamlit Cloud Team** ($250/month):
- 4 GB RAM
- 2 CPU cores
- More apps
- Priority support

**Benefits for this app**:
- Scan 1000+ stocks
- Faster execution
- More reliable

## Security Best Practices

### ✅ DO:
- Use app passwords, not Gmail password
- Keep secrets in Streamlit Cloud only
- Use .gitignore for sensitive files
- Regularly rotate passwords

### ❌ DON'T:
- Commit secrets.toml to GitHub
- Share app password publicly
- Use personal email password
- Store credentials in code

## Support Resources

### Streamlit Cloud
- Docs: [docs.streamlit.io](https://docs.streamlit.io)
- Community: [discuss.streamlit.io](https://discuss.streamlit.io)
- Status: [status.streamlit.io](https://status.streamlit.io)

### GitHub
- Docs: [docs.github.com](https://docs.github.com)
- Help: [support.github.com](https://support.github.com)

### Gmail App Passwords
- Guide: [support.google.com/mail/answer/185833](https://support.google.com/mail/answer/185833)

## Success Checklist

After deployment, verify:

- [ ] App is running on Streamlit Cloud
- [ ] Custom URL is accessible
- [ ] Email configuration saved
- [ ] Stocks loaded successfully
- [ ] Scanner shows 🟢 Active
- [ ] Market status displaying correctly
- [ ] Logs show scan activity
- [ ] First email alert received (when pattern detected)
- [ ] Active Patterns tab populating
- [ ] Statistics tab showing data

## Next Steps

1. **Monitor first week**: Watch for patterns, check alerts
2. **Fine-tune stock list**: Add high-momentum stocks
3. **Adjust parameters**: If too many/few alerts
4. **Share feedback**: Report issues, suggest improvements
5. **Scale gradually**: Add more stocks as comfortable

---

## Quick Deploy Commands

```bash
# 1. Clone/create repo
git init
git add .
git commit -m "Initial commit"

# 2. Push to GitHub
git remote add origin https://github.com/USERNAME/stock-pattern-scanner.git
git push -u origin main

# 3. Deploy on Streamlit Cloud
# Go to share.streamlit.io → New app → Configure → Deploy!
```

**Estimated deployment time**: 15-30 minutes

**You're all set! Happy pattern hunting! 📈🚀**
