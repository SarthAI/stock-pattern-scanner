# ⚡ Quick Start Guide

Get the Stock Pattern Scanner running in 10 minutes!

## 🚀 Super Quick Setup (Local)

### Step 1: Install Dependencies (2 min)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Run Setup Script (1 min)

```bash
python setup.py
```

This creates:
- `.streamlit/` directory
- `secrets.toml` template
- `config.toml` file

### Step 3: Configure Email (3 min)

1. **Get Gmail App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Generate password for "Mail"
   - Copy 16-character password

2. **Edit `.streamlit/secrets.toml`**:
   ```toml
   SENDER_EMAIL = "your-email@gmail.com"
   SENDER_PASSWORD = "abcd efgh ijkl mnop"  # Your app password
   RECIPIENT_EMAIL = "alerts@gmail.com"     # Where to receive alerts
   ```

### Step 4: Test Email (1 min)

```bash
python test_email.py
```

Enter your credentials and verify test email is received.

### Step 5: Run the App (1 min)

```bash
streamlit run app.py
```

Browser opens to: http://localhost:8501

### Step 6: Configure & Start (2 min)

1. **Load Stocks**:
   - Sidebar → "Stock List"
   - Paste symbols (one per line):
     ```
     RELIANCE
     TCS
     INFY
     ```
   - Click "Load Stocks"

2. **Start Scanner**:
   - Click "▶️ Start"
   - Status shows 🟢 Active

**Done! Scanner is now running!** 🎉

---

## ☁️ Super Quick Deploy (Streamlit Cloud)

### Prerequisites (5 min)

1. **GitHub Account**: [github.com](https://github.com)
2. **Upload Project**:
   - Create new repository
   - Upload all files
   - Don't upload `secrets.toml`!

3. **Gmail App Password**: See Step 3 above

### Deploy (5 min)

1. **Go to**: [share.streamlit.io](https://share.streamlit.io)

2. **New App**:
   - Repository: `your-username/stock-pattern-scanner`
   - Branch: `main`
   - File: `app.py`

3. **Add Secrets** (in Advanced settings):
   ```toml
   SENDER_EMAIL = "your-email@gmail.com"
   SENDER_PASSWORD = "your-app-password"
   RECIPIENT_EMAIL = "alerts@gmail.com"
   ```

4. **Click "Deploy!"**

5. **Wait 2-3 minutes** → App is live!

6. **Configure**:
   - Load stock list
   - Click "Start"

**Live! 🚀**

---

## 📊 Verify It's Working

### Check 1: Status Indicators

- ✅ Email configured: Green checkmark
- ✅ Stocks loaded: Shows count
- ✅ Scanner active: 🟢 Active
- ✅ Market status: Shows open/closed

### Check 2: Logs

Look for:
```
INFO - Scheduler started successfully
INFO - Starting TIER1 scan at ...
INFO - Fetched 252 rows for RELIANCE.NS
```

### Check 3: Wait for Alerts

- Patterns take time to form
- First alert may take hours/days
- Check "Active Patterns" tab for detections

---

## 🎯 Your First Alert

When you receive **BREAKOUT CONFIRMED** email:

1. ✅ Read entry price
2. ✅ Set stop loss immediately
3. ✅ Note all 3 targets
4. ✅ Execute trade (if you wish)
5. ✅ Book profits at targets

**Example**:
```
🚨 BREAKOUT CONFIRMED! BUY RELIANCE NOW!

Entry: ₹2,450
Stop Loss: ₹2,400
Target 1: ₹2,500 (Book 30%)
Target 2: ₹2,550 (Book 40%)
Target 3: ₹2,600 (Book 30%)
```

---

## 🛠️ Common Issues

### "Email not sending"
→ Check app password is 16 chars, no spaces
→ Run `python test_email.py`

### "No patterns detected"
→ Normal! Patterns are rare
→ Check market is open (9:15 AM - 3:30 PM IST)
→ Wait 24-48 hours

### "App crashed"
→ Too many stocks (reduce to <300)
→ Check logs for errors

### "Can't install dependencies"
→ Update pip: `pip install --upgrade pip`
→ Try: `pip install -r requirements.txt --no-cache-dir`

---

## 📚 Learn More

- **Full README**: [README.md](README.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Pattern Details**: See README "Pattern Detection Logic"

---

## 🎓 Pro Tips

### 1. Stock Selection

**Good**:
- High liquidity stocks (Nifty 50)
- Active sectors
- Trending stocks

**Avoid**:
- Low volume stocks
- Penny stocks
- Illiquid derivatives

### 2. Pattern Strength

Only trade patterns with:
- ✅ Strength score ≥ 70
- ✅ Volume confirmed
- ✅ Market score ≥ 60

### 3. Risk Management

- Never risk >2% per trade
- Always use stop loss
- Book partial profits at targets
- Trail stop loss after T1

### 4. Best Results

Scanner works best:
- During trending markets
- For large-cap stocks
- With 100-300 stock watchlist
- When market score >60

---

## 🚀 Next Steps

1. **Week 1**: Monitor alerts, don't trade yet
2. **Week 2**: Paper trade alerts, track results
3. **Week 3**: Start small with real trades
4. **Week 4**: Scale up if successful

---

## 📞 Need Help?

1. Check logs: `stock_scanner.log`
2. Review README troubleshooting section
3. Test email separately: `python test_email.py`
4. Verify secrets configuration

---

## ⚠️ Important Reminder

**This is NOT financial advice!**

- Educational tool only
- Do your own research
- Trade at your own risk
- Never invest more than you can afford to lose

---

**Happy Pattern Hunting! 📈**

*Estimated setup time: 10-15 minutes*
*First alert: Hours to days (depends on market)*
