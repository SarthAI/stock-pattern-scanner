# 📈 Stock Pattern Detection & Alert System

Automated stock pattern detection system for NSE (Indian stocks) with real-time email alerts. Detects 8 bullish chart patterns using multi-tier scanning and sends HTML-formatted email alerts for trading opportunities.

## 🎯 Features

### Pattern Detection (8 Bullish Patterns)
1. **Double Bottom (W Pattern)** - Bullish reversal
2. **Inverse Head & Shoulders** - Bullish reversal
3. **Ascending Triangle** - Bullish continuation
4. **Bull Flags & Pennants** - Bullish continuation
5. **Cup & Handle** - Bullish continuation
6. **Triple Bottom** - Strong bullish reversal
7. **Rising Wedge** - Potential breakout
8. **Symmetrical Triangle** - Directional breakout

### Multi-Tier Scanning System
- **TIER 1**: Full scan 4-5 times daily during market hours
- **TIER 2**: Forming patterns check every 30 minutes
- **TIER 3**: Imminent breakouts every 5 minutes
- **TIER 4**: Post-breakout tracking every 30 minutes

### Email Alerts (5 Types)
1. 📊 **PATTERN FORMING** - Initial detection
2. ⚠️ **NEAR BREAKOUT** - Within 2% of breakout
3. 🚨 **BREAKOUT IMMINENT** - Within 0.5% + volume surge
4. 🚨🚨🚨 **BREAKOUT CONFIRMED** - BUY signal with entry/exit levels
5. 🎯 **TARGET HIT** - Profit booking alerts

### Technical Features
- Pattern strength scoring (0-100)
- Volume analysis (20-day average comparison)
- Market condition scoring (Nifty, VIX, sector trends)
- Risk-reward calculation (minimum 1:2 ratio)
- Support/resistance validation
- SQLite persistence for pattern tracking

## 📋 Requirements

- Python 3.9 or higher
- Gmail account (for sending alerts)
- Internet connection (for market data)

## 🚀 Installation

### Local Setup

1. **Clone or download the repository**
```bash
git clone <repository-url>
cd stock-pattern-scanner
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure email credentials**

Create `.streamlit/secrets.toml`:
```toml
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-specific-password"
RECIPIENT_EMAIL = "recipient-email@gmail.com"
```

**Important**: Use Google App Password, not your regular Gmail password!
- Go to: https://myaccount.google.com/apppasswords
- Create app password for "Mail"
- Use that 16-character password

5. **Run the application**
```bash
streamlit run app.py
```

6. **Access the app**
Open browser to: http://localhost:8501

## ☁️ Streamlit Cloud Deployment

### Step 1: Prepare Repository

1. **Create GitHub repository**
   - Upload all files to GitHub
   - Ensure `.gitignore` excludes secrets

2. **Required files for deployment**:
   - `app.py` (main application)
   - `pattern_detector.py`
   - `email_alerts.py`
   - `market_utils.py`
   - `data_manager.py`
   - `requirements.txt`
   - `.streamlit/config.toml` (optional, for theme)

### Step 2: Deploy to Streamlit Cloud

1. **Go to** [share.streamlit.io](https://share.streamlit.io)

2. **Sign in** with GitHub

3. **New app**:
   - Repository: `your-username/stock-pattern-scanner`
   - Branch: `main`
   - Main file path: `app.py`

4. **Advanced settings**:
   - Python version: 3.9+
   - Click "Secrets" and add:
   ```toml
   SENDER_EMAIL = "your-email@gmail.com"
   SENDER_PASSWORD = "your-app-password"
   RECIPIENT_EMAIL = "recipient@gmail.com"
   ```

5. **Deploy!**

### Step 3: Configure Stock List

1. In the Streamlit app sidebar, expand "Stock List"
2. Enter stock symbols (one per line, without .NS suffix):
   ```
   RELIANCE
   TCS
   INFY
   HDFCBANK
   ICICIBANK
   ```
3. Click "Load Stocks"

### Step 4: Start Scanning

1. Verify email configuration is saved
2. Click "▶️ Start" button
3. Scanner will run during market hours (9:15 AM - 3:30 PM IST)

## 📊 Usage Guide

### Dashboard Overview

**Active Patterns Tab**:
- View all detected patterns
- Filter by pattern type, state, and strength
- See current price, breakout point, and distance
- Monitor pattern status in real-time

**Recent Alerts Tab**:
- View email alert history
- See pattern details and trigger prices
- Track alert timestamps

**Statistics Tab**:
- Total patterns detected
- Confirmed breakouts count
- Success rate
- Pattern distribution chart

### Email Alert Flow

1. **Pattern Forming** → Initial detection, start monitoring
2. **Near Breakout** → Prepare order, watch closely
3. **Breakout Imminent** → Get ready, breakout expected soon
4. **Breakout Confirmed** → **BUY NOW** with detailed trade plan
5. **Target Hit** → Book partial profits, trail stop loss

### Pattern Strength Scoring

Each pattern gets a score of 0-100:
- **30 points**: Symmetry/Quality
- **20 points**: Peak height/Depth
- **25 points**: Volume confirmation
- **15 points**: Market conditions
- **10 points**: Time spacing/Structure

**Minimum recommended score**: 50+
**High confidence**: 70+

## ⚙️ Configuration

### Market Hours
- **Trading Days**: Monday - Friday
- **Market Hours**: 9:15 AM - 3:30 PM IST
- Scanning automatically pauses outside market hours

### Scan Schedule (Automatic)
- **TIER 1**: 9:20, 11:20, 13:20, 15:20 (4x daily)
- **TIER 2**: Every 30 minutes (9:00-15:30)
- **TIER 3**: Every 5 minutes (9:00-15:30)
- **TIER 4**: Every 30 minutes at :15 and :45

### Pattern States
1. **FORMING**: Pattern detected, not confirmed
2. **NEAR_BREAKOUT**: Within 1-2% of breakout point
3. **BREAKOUT_IMMINENT**: Within 0.5% + volume building (>1.5x avg)
4. **BREAKOUT_CONFIRMED**: Price closed above breakout with volume (>1.3x avg)

## 🎓 Pattern Detection Logic

### Example: Double Bottom (W Pattern)

**Bottom Detection**:
- Use LOW price for pattern shape
- Validate with CLOSE (wick_ratio > 0.6 for strong bottoms)
- Bottom symmetry tolerance: ≤3% difference
- Peak height: minimum 3% above bottoms
- Time spacing: 10-60 days between bottoms
- Second bottom must NOT be >3% lower than first

**Breakout Conditions**:
- Price breaks above neckline (peak)
- Volume confirmation: >1.3x 20-day average
- Close above breakout point

**Targets**:
- Target 1: 38.2% of pattern height
- Target 2: 61.8% of pattern height
- Target 3: 100% of pattern height

**Stop Loss**: 3% below lowest bottom

## 📧 Email Alert Templates

### Breakout Confirmed Alert (Example)

```
Subject: 🚨🚨🚨 BREAKOUT CONFIRMED! BUY RELIANCE NOW! 🚨🚨🚨

Entry Price: ₹2,450.00
Stop Loss: ₹2,400.00
Target 1: ₹2,500.00 (Book 30%)
Target 2: ₹2,550.00 (Book 40%)
Target 3: ₹2,600.00 (Book 30%)

Risk-Reward: 1:3.0
Volume: ✅ CONFIRMED
```

## 🔧 Troubleshooting

### Common Issues

**1. No data fetching**
- Check internet connection
- Verify stock symbols have .NS suffix in code
- yfinance API may have rate limits - wait and retry

**2. Email not sending**
- Verify Gmail app password is correct
- Check "Less secure app access" is enabled (if using old Gmail)
- Ensure SMTP settings are correct (smtp.gmail.com:587)
- Check firewall/antivirus blocking port 587

**3. Scanner not running**
- Verify market hours (Mon-Fri, 9:15 AM - 3:30 PM IST)
- Check scheduler is started (look for "Active" status)
- Review logs in `stock_scanner.log`

**4. Streamlit Cloud issues**
- Free tier has resource limits (1 GB RAM)
- Large stock lists (>500) may need optimization
- Check app logs in Streamlit Cloud dashboard

### Performance Optimization

**For large stock lists (>1000 stocks)**:
1. Reduce scan frequency
2. Split into multiple instances
3. Use caching aggressively
4. Filter stocks by market cap/liquidity

**Memory optimization**:
- Scan data is cached for 5 minutes
- Database auto-cleans patterns older than 30 days
- Limit active patterns per stock to 1

## 📝 Sample Stock Lists

### Nifty 50 (Large Cap)
```
RELIANCE
TCS
HDFCBANK
INFY
ICICIBANK
HINDUNILVR
ITC
SBIN
BHARTIARTL
KOTAKBANK
```

### Mid Cap
```
ADANIPORTS
GRASIM
INDIGO
SHREECEM
ULTRACEMCO
```

### Banking
```
HDFCBANK
ICICIBANK
SBIN
KOTAKBANK
AXISBANK
INDUSINDBK
BANDHANBNK
```

## 📈 Market Condition Scoring

The system scores market conditions (0-100):

1. **Nifty Trend** (30 points)
   - Price > 50-day MA: +15
   - Price > 200-day MA: +10
   - 5-day momentum: +5

2. **Sector Trend** (25 points)
   - Bank Nifty > 50-day MA: +15
   - Positive momentum: +10

3. **VIX Score** (20 points)
   - VIX < 12: +20 (very low volatility)
   - VIX 12-15: +15 (low)
   - VIX 15-20: +10 (moderate)

4. **Market Breadth** (15 points)
   - Both Nifty & Bank Nifty up: +15

5. **FII Activity** (10 points)
   - High volume + price up: +10

**Score Interpretation**:
- 80-100: Excellent conditions
- 60-80: Good conditions
- 40-60: Neutral
- 20-40: Weak conditions
- 0-20: Poor conditions

## 🚨 Important Notes

### Risk Disclaimer
⚠️ **This is NOT financial advice. Trading involves risk of loss.**
- Use this tool for informational purposes only
- Always do your own research (DYOR)
- Never invest more than you can afford to lose
- Past patterns don't guarantee future results
- Pattern success rate varies by market conditions

### Data Accuracy
- Data from yfinance may have delays
- Pattern detection is algorithmic, not guaranteed
- Always verify patterns manually on charts
- Cross-check with trading terminal before executing

### Rate Limits
- yfinance has rate limits (exact limits vary)
- System implements 2-second delays every 50 stocks
- Free tier is limited; consider paid data source for production

## 🛠️ Development

### Project Structure
```
stock-pattern-scanner/
├── app.py                  # Main Streamlit app
├── pattern_detector.py     # Pattern detection logic
├── email_alerts.py         # Email alert system
├── market_utils.py         # Market utilities
├── data_manager.py         # Data & database management
├── requirements.txt        # Python dependencies
├── .streamlit/
│   ├── secrets.toml        # Email credentials (DO NOT COMMIT)
│   └── config.toml         # App configuration
├── .gitignore             # Git ignore file
├── README.md              # This file
└── stock_patterns.db      # SQLite database (auto-created)
```

### Extending the System

**Add new patterns**:
1. Create detection method in `pattern_detector.py`
2. Follow existing pattern structure
3. Return pattern dict with required fields
4. Add to `detect_all_patterns()` method

**Add new alert types**:
1. Create alert method in `email_alerts.py`
2. Design HTML template
3. Hook into pattern state changes

**Modify scan schedule**:
1. Edit `setup_scheduler()` in `app.py`
2. Use cron syntax for timing
3. Restart app to apply changes

## 📞 Support

### Getting Help
- Check logs: `stock_scanner.log`
- Review Streamlit app logs
- Verify configuration in secrets.toml
- Test email sending separately

### Contributing
Pull requests welcome! Please:
1. Follow existing code style
2. Add comments for complex logic
3. Test thoroughly before submitting
4. Update README if needed

## 📄 License

This project is provided as-is for educational purposes.

## 🙏 Acknowledgments

- Market data: [yfinance](https://github.com/ranaroussi/yfinance)
- Web framework: [Streamlit](https://streamlit.io)
- Scheduling: [APScheduler](https://apscheduler.readthedocs.io)

---

## Quick Start Checklist

- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Gmail app password created
- [ ] `.streamlit/secrets.toml` configured
- [ ] Stock list prepared
- [ ] Email configuration tested
- [ ] App started (`streamlit run app.py`)
- [ ] Scanner activated (▶️ Start button)
- [ ] First alert received 🎉

**Happy Trading! 📈**
