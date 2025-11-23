"""
Stock Pattern Detection & Alert System
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
from datetime import datetime, time as dt_time
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import sqlite3
import logging
from typing import List, Dict
import time

from pattern_detector import PatternDetector
from email_alerts import EmailAlertSystem
from market_utils import MarketUtils
from data_manager import DataManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_scanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Stock Pattern Scanner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = None
if 'scanning_active' not in st.session_state:
    st.session_state.scanning_active = False
if 'stock_list' not in st.session_state:
    st.session_state.stock_list = []
if 'last_scan_time' not in st.session_state:
    st.session_state.last_scan_time = None
if 'scan_count' not in st.session_state:
    st.session_state.scan_count = 0

# Initialize components
@st.cache_resource
def init_components():
    """Initialize core components"""
    data_manager = DataManager()
    pattern_detector = PatternDetector()
    market_utils = MarketUtils()
    return data_manager, pattern_detector, market_utils

data_manager, pattern_detector, market_utils = init_components()

def get_email_system():
    """Get email system with current credentials"""
    if 'email_configured' in st.session_state and st.session_state.email_configured:
        try:
            return EmailAlertSystem(
                smtp_server=st.session_state.get('smtp_server', 'smtp.gmail.com'),
                smtp_port=st.session_state.get('smtp_port', 587),
                sender_email=st.session_state.get('sender_email', ''),
                sender_password=st.session_state.get('sender_password', ''),
                recipient_email=st.session_state.get('recipient_email', '')
            )
        except Exception as e:
            logger.error(f"Failed to initialize email system: {e}")
            return None
    return None

def perform_scan(tier: str):
    """Execute pattern scanning based on tier"""
    if not st.session_state.scanning_active:
        return

    if not market_utils.is_market_open():
        logger.info(f"Market closed - skipping {tier} scan")
        return

    try:
        logger.info(f"Starting {tier} scan at {datetime.now()}")
        st.session_state.last_scan_time = datetime.now()
        st.session_state.scan_count += 1

        email_system = get_email_system()
        stocks = st.session_state.stock_list

        if not stocks:
            logger.warning("No stocks to scan")
            return

        # Get market condition score
        market_score = market_utils.get_market_condition_score()
        logger.info(f"Market condition score: {market_score}")

        scanned = 0
        patterns_found = 0

        for symbol in stocks:
            try:
                # Add .NS suffix for NSE stocks
                nse_symbol = symbol if symbol.endswith('.NS') else f"{symbol}.NS"

                # Fetch data
                df = data_manager.fetch_stock_data(nse_symbol, period='1y')
                if df is None or len(df) < 60:
                    continue

                # Detect patterns based on tier
                if tier == 'TIER1':
                    # Full pattern detection
                    patterns = pattern_detector.detect_all_patterns(df, nse_symbol, market_score)
                elif tier == 'TIER2':
                    # Check forming patterns
                    patterns = pattern_detector.check_forming_patterns(df, nse_symbol, market_score)
                elif tier == 'TIER3':
                    # Check imminent breakouts
                    patterns = pattern_detector.check_imminent_breakouts(df, nse_symbol, market_score)
                elif tier == 'TIER4':
                    # Check confirmed breakouts
                    patterns = pattern_detector.check_confirmed_breakouts(df, nse_symbol, market_score)
                else:
                    patterns = []

                # Process detected patterns
                for pattern in patterns:
                    patterns_found += 1
                    data_manager.save_pattern(pattern)

                    # Send email alerts
                    if email_system:
                        try:
                            email_system.send_pattern_alert(pattern)
                        except Exception as e:
                            logger.error(f"Failed to send email for {nse_symbol}: {e}")

                scanned += 1

                # Rate limiting
                if scanned % 50 == 0:
                    time.sleep(2)

            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                continue

        logger.info(f"{tier} scan completed: {scanned} stocks scanned, {patterns_found} patterns found")

    except Exception as e:
        logger.error(f"Error in {tier} scan: {e}")

def setup_scheduler():
    """Setup APScheduler for multi-tier scanning"""
    if st.session_state.scheduler is not None:
        st.session_state.scheduler.shutdown()

    scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Kolkata'))

    # TIER 1: Full scan 4-5 times during market hours
    scheduler.add_job(
        lambda: perform_scan('TIER1'),
        CronTrigger(day_of_week='mon-fri', hour='9,11,13,15', minute='20'),
        id='tier1_scan'
    )

    # TIER 2: Forming patterns every 30 minutes
    scheduler.add_job(
        lambda: perform_scan('TIER2'),
        CronTrigger(day_of_week='mon-fri', hour='9-15', minute='*/30'),
        id='tier2_scan'
    )

    # TIER 3: Imminent breakouts every 5 minutes
    scheduler.add_job(
        lambda: perform_scan('TIER3'),
        CronTrigger(day_of_week='mon-fri', hour='9-15', minute='*/5'),
        id='tier3_scan'
    )

    # TIER 4: Post-breakout tracking every 30 minutes
    scheduler.add_job(
        lambda: perform_scan('TIER4'),
        CronTrigger(day_of_week='mon-fri', hour='9-15', minute='15,45'),
        id='tier4_scan'
    )

    scheduler.start()
    st.session_state.scheduler = scheduler
    logger.info("Scheduler started successfully")

# ===== STREAMLIT UI =====

st.title("📈 Stock Pattern Detection & Alert System")
st.markdown("---")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Email Configuration
    with st.expander("📧 Email Settings", expanded=False):
        smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
        smtp_port = st.number_input("SMTP Port", value=587, min_value=1, max_value=65535)
        sender_email = st.text_input("Sender Email", value=st.secrets.get("SENDER_EMAIL", "") if hasattr(st, 'secrets') else "")
        sender_password = st.text_input("App Password", type="password", value=st.secrets.get("SENDER_PASSWORD", "") if hasattr(st, 'secrets') else "")
        recipient_email = st.text_input("Recipient Email", value=st.secrets.get("RECIPIENT_EMAIL", "") if hasattr(st, 'secrets') else "")

        if st.button("Save Email Config"):
            st.session_state.smtp_server = smtp_server
            st.session_state.smtp_port = smtp_port
            st.session_state.sender_email = sender_email
            st.session_state.sender_password = sender_password
            st.session_state.recipient_email = recipient_email
            st.session_state.email_configured = True
            st.success("✅ Email configuration saved!")

    # Stock List Configuration
    with st.expander("📊 Stock List", expanded=True):
        st.markdown("Enter stock symbols (one per line, without .NS suffix):")
        stock_input = st.text_area(
            "Stock Symbols",
            height=200,
            placeholder="RELIANCE\nTCS\nINFY\nHDFC\nICICIBANK",
            value="\n".join(st.session_state.stock_list) if st.session_state.stock_list else ""
        )

        if st.button("Load Stocks"):
            stocks = [s.strip().upper() for s in stock_input.split('\n') if s.strip()]
            st.session_state.stock_list = stocks
            st.success(f"✅ Loaded {len(stocks)} stocks")

    st.markdown("---")

    # Control Buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶️ Start", use_container_width=True, disabled=st.session_state.scanning_active):
            if not st.session_state.stock_list:
                st.error("Please load stock list first!")
            elif not st.session_state.get('email_configured', False):
                st.error("Please configure email settings!")
            else:
                st.session_state.scanning_active = True
                setup_scheduler()
                st.success("✅ Scanner started!")
                st.rerun()

    with col2:
        if st.button("⏹️ Stop", use_container_width=True, disabled=not st.session_state.scanning_active):
            st.session_state.scanning_active = False
            if st.session_state.scheduler:
                st.session_state.scheduler.shutdown()
                st.session_state.scheduler = None
            st.warning("⏹️ Scanner stopped!")
            st.rerun()

    # Status
    st.markdown("---")
    st.subheader("📊 Status")

    if st.session_state.scanning_active:
        st.success("🟢 Active")
    else:
        st.error("🔴 Inactive")

    st.metric("Stocks Loaded", len(st.session_state.stock_list))
    st.metric("Total Scans", st.session_state.scan_count)

    if st.session_state.last_scan_time:
        st.text(f"Last Scan:\n{st.session_state.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Market Status
    is_open, status_msg = market_utils.is_market_open(return_message=True)
    if is_open:
        st.success(f"🟢 {status_msg}")
    else:
        st.warning(f"🟡 {status_msg}")

# Main Content Area
tab1, tab2, tab3, tab4 = st.tabs(["📊 Active Patterns", "📜 Recent Alerts", "📈 Statistics", "ℹ️ About"])

with tab1:
    st.header("Active Patterns")

    # Fetch active patterns from database
    patterns_df = data_manager.get_active_patterns()

    if not patterns_df.empty:
        # Filter controls
        col1, col2, col3 = st.columns(3)
        with col1:
            pattern_filter = st.multiselect("Pattern Type", options=patterns_df['pattern_type'].unique(), default=patterns_df['pattern_type'].unique())
        with col2:
            state_filter = st.multiselect("State", options=patterns_df['state'].unique(), default=patterns_df['state'].unique())
        with col3:
            min_strength = st.slider("Min Strength", 0, 100, 50)

        # Apply filters
        filtered_df = patterns_df[
            (patterns_df['pattern_type'].isin(pattern_filter)) &
            (patterns_df['state'].isin(state_filter)) &
            (patterns_df['strength_score'] >= min_strength)
        ]

        # Display patterns
        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "strength_score": st.column_config.ProgressColumn("Strength", min_value=0, max_value=100),
                "current_price": st.column_config.NumberColumn("Price", format="₹%.2f"),
                "breakout_point": st.column_config.NumberColumn("Breakout", format="₹%.2f"),
                "distance_pct": st.column_config.NumberColumn("Distance %", format="%.2f%%"),
            },
            hide_index=True
        )

        st.metric("Total Active Patterns", len(filtered_df))
    else:
        st.info("No active patterns detected yet. Start scanning to find patterns!")

with tab2:
    st.header("Recent Alerts")

    alerts_df = data_manager.get_recent_alerts(limit=50)

    if not alerts_df.empty:
        for _, alert in alerts_df.iterrows():
            with st.expander(f"{alert['symbol']} - {alert['pattern_type']} - {alert['alert_type']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                col1.metric("Price", f"₹{alert['price']:.2f}")
                col2.metric("Strength", f"{alert['strength_score']:.0f}")
                col3.metric("Time", alert['timestamp'])

                if alert.get('message'):
                    st.text(alert['message'])
    else:
        st.info("No alerts yet. Alerts will appear here once patterns are detected.")

with tab3:
    st.header("Pattern Statistics")

    stats = data_manager.get_pattern_statistics()

    if stats:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Patterns Detected", stats.get('total_patterns', 0))
        col2.metric("Confirmed Breakouts", stats.get('confirmed_breakouts', 0))
        col3.metric("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
        col4.metric("Avg Strength", f"{stats.get('avg_strength', 0):.1f}")

        # Pattern distribution
        if 'pattern_distribution' in stats and stats['pattern_distribution']:
            st.subheader("Pattern Distribution")
            dist_df = pd.DataFrame(list(stats['pattern_distribution'].items()), columns=['Pattern', 'Count'])
            st.bar_chart(dist_df.set_index('Pattern'))
    else:
        st.info("No statistics available yet. Start scanning to generate statistics!")

with tab4:
    st.header("About This System")

    st.markdown("""
    ### 🎯 Pattern Detection System

    This system automatically detects 8 bullish chart patterns in NSE stocks:

    1. **Double Bottom (W Pattern)** - Bullish reversal
    2. **Inverse Head & Shoulders** - Bullish reversal
    3. **Ascending Triangle** - Bullish continuation
    4. **Bull Flags & Pennants** - Bullish continuation
    5. **Cup & Handle** - Bullish continuation
    6. **Triple Bottom** - Strong bullish reversal
    7. **Rising Wedge** - Potential breakout
    8. **Symmetrical Triangle** - Directional breakout

    ### ⚡ Multi-Tier Scanning

    - **TIER 1**: Full scan 4-5x daily (market hours)
    - **TIER 2**: Forming patterns check every 30 min
    - **TIER 3**: Imminent breakouts every 5 min
    - **TIER 4**: Post-breakout tracking every 30 min

    ### 📧 Alert Types

    - 📊 **PATTERN FORMING**: Initial detection
    - ⚠️ **NEAR BREAKOUT**: Within 2% of breakout
    - 🚨 **BREAKOUT IMMINENT**: Within 0.5% + volume surge
    - 🚨🚨🚨 **BREAKOUT CONFIRMED**: BUY signal with entry/exit levels
    - 🎯 **TARGET HIT**: Profit booking alerts

    ### 📊 Pattern Scoring (0-100)

    - Symmetry: 30 points
    - Peak height: 20 points
    - Volume confirmation: 25 points
    - Market conditions: 15 points
    - Time spacing: 10 points

    ### ⏰ Market Hours

    Scanning active: Monday-Friday, 9:15 AM - 3:30 PM IST
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    Stock Pattern Detection System v1.0 | Market data powered by yfinance
    </div>
    """,
    unsafe_allow_html=True
)
