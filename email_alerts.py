"""
Email Alert System
Sends HTML-formatted email alerts for different pattern states
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailAlertSystem:
    """Manages email alerts for pattern detection"""

    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str,
                 sender_password: str, recipient_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email

    def send_pattern_alert(self, pattern: Dict) -> bool:
        """
        Send email alert based on pattern state

        Alert Types:
        - FORMING: Initial pattern detection
        - NEAR_BREAKOUT: Within 2% of breakout
        - BREAKOUT_IMMINENT: Within 0.5% + volume
        - BREAKOUT_CONFIRMED: Buy signal
        """
        try:
            state = pattern['state']

            if state == 'FORMING':
                return self._send_forming_alert(pattern)
            elif state == 'NEAR_BREAKOUT':
                return self._send_near_breakout_alert(pattern)
            elif state == 'BREAKOUT_IMMINENT':
                return self._send_imminent_alert(pattern)
            elif state == 'BREAKOUT_CONFIRMED':
                return self._send_confirmed_alert(pattern)

            return False

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False

    def _send_forming_alert(self, pattern: Dict) -> bool:
        """A) PATTERN FORMING - Initial detection"""
        symbol = pattern['symbol'].replace('.NS', '')
        pattern_name = pattern['pattern_type'].replace('_', ' ').title()

        subject = f"📊 PATTERN FORMING: {symbol} - {pattern_name}"

        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .metric {{ background-color: #f5f5f5; padding: 10px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
                .label {{ font-weight: bold; color: #666; }}
                .value {{ font-size: 18px; color: #333; }}
                .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; }}
                .warning {{ color: #ff9800; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 PATTERN FORMING</h1>
                <h2>{symbol} - {pattern_name}</h2>
            </div>

            <div class="content">
                <p>A bullish <strong>{pattern_name}</strong> pattern has been detected in <strong>{symbol}</strong>.</p>

                <div class="metric">
                    <span class="label">Current Price:</span>
                    <span class="value">₹{pattern['current_price']:.2f}</span>
                </div>

                <div class="metric">
                    <span class="label">Breakout Point:</span>
                    <span class="value">₹{pattern['breakout_point']:.2f}</span>
                </div>

                <div class="metric">
                    <span class="label">Distance to Breakout:</span>
                    <span class="value">{pattern['distance_pct']:.2f}%</span>
                </div>

                <div class="metric">
                    <span class="label">Pattern Strength Score:</span>
                    <span class="value">{pattern['strength_score']}/100</span>
                </div>

                <div class="metric">
                    <span class="label">Invalidation Point:</span>
                    <span class="value warning">₹{pattern['invalidation_point']:.2f}</span>
                </div>

                <hr>

                <h3>📊 Potential Targets</h3>
                <ul>
                    <li><strong>Target 1:</strong> ₹{pattern['target1']:.2f} (+{((pattern['target1']/pattern['current_price']-1)*100):.2f}%)</li>
                    <li><strong>Target 2:</strong> ₹{pattern['target2']:.2f} (+{((pattern['target2']/pattern['current_price']-1)*100):.2f}%)</li>
                    <li><strong>Target 3:</strong> ₹{pattern['target3']:.2f} (+{((pattern['target3']/pattern['current_price']-1)*100):.2f}%)</li>
                </ul>

                <h3>⚠️ Risk Management</h3>
                <ul>
                    <li><strong>Stop Loss:</strong> ₹{pattern['stop_loss']:.2f}</li>
                    <li><strong>Risk:</strong> {((pattern['current_price']-pattern['stop_loss'])/pattern['current_price']*100):.2f}%</li>
                    <li><strong>Reward (Target 3):</strong> {((pattern['target3']-pattern['current_price'])/pattern['current_price']*100):.2f}%</li>
                </ul>

                <p class="warning">⚠️ Pattern is FORMING. Wait for breakout confirmation before taking position.</p>
            </div>

            <div class="footer">
                <p>Generated by Stock Pattern Scanner | {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}</p>
            </div>
        </body>
        </html>
        """

        return self._send_email(subject, body)

    def _send_near_breakout_alert(self, pattern: Dict) -> bool:
        """B) NEAR BREAKOUT - Within 2%"""
        symbol = pattern['symbol'].replace('.NS', '')
        pattern_name = pattern['pattern_type'].replace('_', ' ').title()

        subject = f"⚠️ NEAR BREAKOUT: {symbol} - Only {abs(pattern['distance_pct']):.2f}% Away!"

        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .header {{ background-color: #FF9800; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .metric {{ background-color: #fff3e0; padding: 10px; margin: 10px 0; border-left: 4px solid #FF9800; }}
                .label {{ font-weight: bold; color: #666; }}
                .value {{ font-size: 18px; color: #333; }}
                .action {{ background-color: #ffecb3; padding: 15px; margin: 15px 0; border: 2px solid #FF9800; }}
                .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; }}
                .highlight {{ color: #f44336; font-weight: bold; font-size: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚠️ NEAR BREAKOUT ALERT</h1>
                <h2>{symbol} - {pattern_name}</h2>
                <p class="highlight">Only {abs(pattern['distance_pct']):.2f}% from breakout!</p>
            </div>

            <div class="content">
                <div class="metric">
                    <span class="label">Current Price:</span>
                    <span class="value">₹{pattern['current_price']:.2f}</span>
                </div>

                <div class="metric">
                    <span class="label">Breakout Point:</span>
                    <span class="value">₹{pattern['breakout_point']:.2f}</span>
                </div>

                <div class="metric">
                    <span class="label">Pattern Strength:</span>
                    <span class="value">{pattern['strength_score']}/100</span>
                </div>

                <div class="metric">
                    <span class="label">Volume Status:</span>
                    <span class="value">{'✅ CONFIRMED' if pattern['volume_confirmed'] else '⚠️ BUILDING'}</span>
                </div>

                <hr>

                <div class="action">
                    <h3>📋 Recommended Order Setup</h3>
                    <ul>
                        <li><strong>Entry:</strong> ₹{pattern['breakout_point']:.2f} (on breakout)</li>
                        <li><strong>Stop Loss:</strong> ₹{pattern['stop_loss']:.2f}</li>
                        <li><strong>Target 1:</strong> ₹{pattern['target1']:.2f}</li>
                        <li><strong>Target 2:</strong> ₹{pattern['target2']:.2f}</li>
                        <li><strong>Target 3:</strong> ₹{pattern['target3']:.2f}</li>
                    </ul>

                    <p><strong>Risk-Reward Ratio:</strong> 1:{((pattern['target3']-pattern['breakout_point'])/(pattern['breakout_point']-pattern['stop_loss'])):.2f}</p>
                </div>

                <h3>🎯 Action Items</h3>
                <ol>
                    <li>Add {symbol} to watchlist</li>
                    <li>Monitor volume for surge (need >1.5x average)</li>
                    <li>Prepare buy order at ₹{pattern['breakout_point']:.2f}</li>
                    <li>Set alert at ₹{pattern['breakout_point']*0.995:.2f} (0.5% below breakout)</li>
                </ol>

                <p class="highlight">⚠️ Be ready! Breakout could happen anytime.</p>
            </div>

            <div class="footer">
                <p>Generated by Stock Pattern Scanner | {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}</p>
            </div>
        </body>
        </html>
        """

        return self._send_email(subject, body)

    def _send_imminent_alert(self, pattern: Dict) -> bool:
        """C) BREAKOUT IMMINENT - Within 0.5% + volume building"""
        symbol = pattern['symbol'].replace('.NS', '')
        pattern_name = pattern['pattern_type'].replace('_', ' ').title()

        subject = f"🚨🚨 IMMINENT BREAKOUT: {symbol} - GET READY NOW!"

        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .metric {{ background-color: #ffebee; padding: 10px; margin: 10px 0; border-left: 4px solid #f44336; }}
                .label {{ font-weight: bold; color: #666; }}
                .value {{ font-size: 20px; color: #f44336; font-weight: bold; }}
                .action {{ background-color: #ffcdd2; padding: 15px; margin: 15px 0; border: 3px solid #f44336; }}
                .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; }}
                .urgent {{ color: #f44336; font-weight: bold; font-size: 24px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚨🚨 IMMINENT BREAKOUT 🚨🚨</h1>
                <h2>{symbol} - {pattern_name}</h2>
                <p class="urgent">BREAKOUT EXPECTED ANY MOMENT!</p>
            </div>

            <div class="content">
                <p class="urgent">Only ₹{abs(pattern['breakout_point']-pattern['current_price']):.2f} away from breakout!</p>

                <div class="metric">
                    <span class="label">Current Price:</span>
                    <span class="value">₹{pattern['current_price']:.2f}</span>
                </div>

                <div class="metric">
                    <span class="label">Breakout Point:</span>
                    <span class="value">₹{pattern['breakout_point']:.2f}</span>
                </div>

                <div class="metric">
                    <span class="label">Volume Status:</span>
                    <span class="value">🔥 BUILDING / SURGING</span>
                </div>

                <div class="metric">
                    <span class="label">Pattern Strength:</span>
                    <span class="value">{pattern['strength_score']}/100</span>
                </div>

                <hr>

                <div class="action">
                    <h3>⚡ IMMEDIATE ACTION REQUIRED</h3>
                    <ol>
                        <li><strong>OPEN TRADING TERMINAL NOW</strong></li>
                        <li><strong>Place BUY order at:</strong> ₹{pattern['breakout_point']:.2f}</li>
                        <li><strong>Set Stop Loss at:</strong> ₹{pattern['stop_loss']:.2f}</li>
                        <li><strong>Monitor 5-min chart</strong></li>
                        <li><strong>Watch for volume confirmation</strong> (need 1.3x+ average)</li>
                    </ol>
                </div>

                <h3>🎯 Trade Setup</h3>
                <table style="width:100%; border-collapse: collapse;">
                    <tr style="background-color:#f5f5f5;">
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Entry Price</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">₹{pattern['breakout_point']:.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Stop Loss</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">₹{pattern['stop_loss']:.2f} (-{((pattern['breakout_point']-pattern['stop_loss'])/pattern['breakout_point']*100):.2f}%)</td>
                    </tr>
                    <tr style="background-color:#f5f5f5;">
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Target 1 (Book 30%)</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">₹{pattern['target1']:.2f} (+{((pattern['target1']-pattern['breakout_point'])/pattern['breakout_point']*100):.2f}%)</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Target 2 (Book 40%)</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">₹{pattern['target2']:.2f} (+{((pattern['target2']-pattern['breakout_point'])/pattern['breakout_point']*100):.2f}%)</td>
                    </tr>
                    <tr style="background-color:#f5f5f5;">
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Target 3 (Book 30%)</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">₹{pattern['target3']:.2f} (+{((pattern['target3']-pattern['breakout_point'])/pattern['breakout_point']*100):.2f}%)</td>
                    </tr>
                </table>

                <p class="urgent">⏰ Stay alert! Breakout can happen in next few minutes!</p>
            </div>

            <div class="footer">
                <p>Generated by Stock Pattern Scanner | {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}</p>
            </div>
        </body>
        </html>
        """

        return self._send_email(subject, body)

    def _send_confirmed_alert(self, pattern: Dict) -> bool:
        """D) BREAKOUT CONFIRMED - BUY SIGNAL"""
        symbol = pattern['symbol'].replace('.NS', '')
        pattern_name = pattern['pattern_type'].replace('_', ' ').title()

        subject = f"🚨🚨🚨 BREAKOUT CONFIRMED! BUY {symbol} NOW! 🚨🚨🚨"

        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; animation: pulse 2s infinite; }}
                @keyframes pulse {{
                    0%, 100% {{ opacity: 1; }}
                    50% {{ opacity: 0.8; }}
                }}
                .content {{ padding: 20px; }}
                .metric {{ background-color: #e8f5e9; padding: 10px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
                .label {{ font-weight: bold; color: #666; }}
                .value {{ font-size: 22px; color: #4CAF50; font-weight: bold; }}
                .action {{ background-color: #c8e6c9; padding: 20px; margin: 15px 0; border: 3px solid #4CAF50; }}
                .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; }}
                .buy-now {{ color: #4CAF50; font-weight: bold; font-size: 28px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚨🚨🚨 BREAKOUT CONFIRMED 🚨🚨🚨</h1>
                <h2>{symbol} - {pattern_name}</h2>
                <p class="buy-now">BUY SIGNAL ACTIVATED!</p>
            </div>

            <div class="content">
                <p class="buy-now">✅ Pattern breakout confirmed with volume!</p>

                <div class="metric">
                    <span class="label">Entry Price:</span>
                    <span class="value">₹{pattern['current_price']:.2f}</span>
                </div>

                <div class="metric">
                    <span class="label">Breakout Point:</span>
                    <span class="value">₹{pattern['breakout_point']:.2f}</span>
                </div>

                <div class="metric">
                    <span class="label">Volume Confirmation:</span>
                    <span class="value">✅ CONFIRMED</span>
                </div>

                <div class="metric">
                    <span class="label">Pattern Strength:</span>
                    <span class="value">{pattern['strength_score']}/100</span>
                </div>

                <hr>

                <div class="action">
                    <h2 style="color:#4CAF50; text-align:center;">📊 TRADE EXECUTION PLAN</h2>

                    <h3>💰 Entry & Exit Levels</h3>
                    <table style="width:100%; border-collapse: collapse; font-size:16px;">
                        <tr style="background-color:#4CAF50; color:white;">
                            <th style="padding:12px; border:1px solid #ddd;">Level</th>
                            <th style="padding:12px; border:1px solid #ddd;">Price</th>
                            <th style="padding:12px; border:1px solid #ddd;">Gain/Loss</th>
                            <th style="padding:12px; border:1px solid #ddd;">Action</th>
                        </tr>
                        <tr style="background-color:#e8f5e9;">
                            <td style="padding:10px; border:1px solid #ddd;"><strong>ENTRY NOW</strong></td>
                            <td style="padding:10px; border:1px solid #ddd;"><strong>₹{pattern['current_price']:.2f}</strong></td>
                            <td style="padding:10px; border:1px solid #ddd;">-</td>
                            <td style="padding:10px; border:1px solid #ddd;"><strong>BUY 100%</strong></td>
                        </tr>
                        <tr>
                            <td style="padding:10px; border:1px solid #ddd;">Stop Loss</td>
                            <td style="padding:10px; border:1px solid #ddd;">₹{pattern['stop_loss']:.2f}</td>
                            <td style="padding:10px; border:1px solid #ddd; color:red;">-{((pattern['current_price']-pattern['stop_loss'])/pattern['current_price']*100):.2f}%</td>
                            <td style="padding:10px; border:1px solid #ddd;">Exit all</td>
                        </tr>
                        <tr style="background-color:#f1f8f4;">
                            <td style="padding:10px; border:1px solid #ddd;">Target 1</td>
                            <td style="padding:10px; border:1px solid #ddd;">₹{pattern['target1']:.2f}</td>
                            <td style="padding:10px; border:1px solid #ddd; color:green;">+{((pattern['target1']-pattern['current_price'])/pattern['current_price']*100):.2f}%</td>
                            <td style="padding:10px; border:1px solid #ddd;">Book 30%</td>
                        </tr>
                        <tr>
                            <td style="padding:10px; border:1px solid #ddd;">Target 2</td>
                            <td style="padding:10px; border:1px solid #ddd;">₹{pattern['target2']:.2f}</td>
                            <td style="padding:10px; border:1px solid #ddd; color:green;">+{((pattern['target2']-pattern['current_price'])/pattern['current_price']*100):.2f}%</td>
                            <td style="padding:10px; border:1px solid #ddd;">Book 40%</td>
                        </tr>
                        <tr style="background-color:#f1f8f4;">
                            <td style="padding:10px; border:1px solid #ddd;">Target 3</td>
                            <td style="padding:10px; border:1px solid #ddd;">₹{pattern['target3']:.2f}</td>
                            <td style="padding:10px; border:1px solid #ddd; color:green;">+{((pattern['target3']-pattern['current_price'])/pattern['current_price']*100):.2f}%</td>
                            <td style="padding:10px; border:1px solid #ddd;">Book 30%</td>
                        </tr>
                    </table>

                    <h3 style="margin-top:20px;">📋 Execution Checklist</h3>
                    <ol style="font-size:16px; line-height:1.8;">
                        <li>✅ <strong>Buy {symbol} at market price</strong> (or limit at ₹{pattern['current_price']:.2f})</li>
                        <li>✅ <strong>Immediately set Stop Loss</strong> at ₹{pattern['stop_loss']:.2f}</li>
                        <li>✅ <strong>Set Target 1 alert</strong> at ₹{pattern['target1']:.2f}</li>
                        <li>✅ <strong>Set Target 2 alert</strong> at ₹{pattern['target2']:.2f}</li>
                        <li>✅ <strong>Set Target 3 alert</strong> at ₹{pattern['target3']:.2f}</li>
                        <li>✅ <strong>Trail stop loss</strong> after Target 1 is hit</li>
                    </ol>

                    <h3 style="margin-top:20px;">📊 Risk-Reward Analysis</h3>
                    <ul style="font-size:16px;">
                        <li><strong>Risk:</strong> ₹{(pattern['current_price']-pattern['stop_loss']):.2f} ({((pattern['current_price']-pattern['stop_loss'])/pattern['current_price']*100):.2f}%)</li>
                        <li><strong>Reward (T3):</strong> ₹{(pattern['target3']-pattern['current_price']):.2f} ({((pattern['target3']-pattern['current_price'])/pattern['current_price']*100):.2f}%)</li>
                        <li><strong>R:R Ratio:</strong> 1:{((pattern['target3']-pattern['current_price'])/(pattern['current_price']-pattern['stop_loss'])):.2f}</li>
                    </ul>
                </div>

                <h3 style="color:#4CAF50;">🎯 Profit Booking Strategy</h3>
                <ol style="font-size:15px;">
                    <li><strong>At Target 1 (₹{pattern['target1']:.2f}):</strong> Book 30% profit, move SL to entry</li>
                    <li><strong>At Target 2 (₹{pattern['target2']:.2f}):</strong> Book 40% more, trail SL to T1</li>
                    <li><strong>At Target 3 (₹{pattern['target3']:.2f}):</strong> Book remaining 30%, trail SL to T2</li>
                </ol>

                <p style="text-align:center; font-size:18px; color:#4CAF50; font-weight:bold; margin-top:20px;">
                    🚀 Act now! Momentum is building! 🚀
                </p>
            </div>

            <div class="footer">
                <p>Generated by Stock Pattern Scanner | {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}</p>
                <p style="color:#666; font-style:italic;">This is not financial advice. Trade at your own risk.</p>
            </div>
        </body>
        </html>
        """

        return self._send_email(subject, body)

    def send_target_hit_alert(self, symbol: str, target_num: int, entry_price: float,
                               target_price: float, current_price: float) -> bool:
        """E) TARGET HIT - Profit booking alert"""
        symbol_clean = symbol.replace('.NS', '')
        profit_pct = ((current_price - entry_price) / entry_price) * 100

        subject = f"🎯 TARGET {target_num} HIT! {symbol_clean} - Book Partial Profits"

        booking_pct = [30, 40, 30][target_num - 1] if target_num <= 3 else 100

        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .metric {{ background-color: #e3f2fd; padding: 10px; margin: 10px 0; border-left: 4px solid #2196F3; }}
                .label {{ font-weight: bold; color: #666; }}
                .value {{ font-size: 20px; color: #2196F3; font-weight: bold; }}
                .action {{ background-color: #bbdefb; padding: 15px; margin: 15px 0; border: 2px solid #2196F3; }}
                .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 TARGET {target_num} HIT!</h1>
                <h2>{symbol_clean}</h2>
                <p style="font-size:24px;">Book {booking_pct}% Profit Now!</p>
            </div>

            <div class="content">
                <div class="metric">
                    <span class="label">Entry Price:</span>
                    <span class="value">₹{entry_price:.2f}</span>
                </div>

                <div class="metric">
                    <span class="label">Current Price:</span>
                    <span class="value">₹{current_price:.2f}</span>
                </div>

                <div class="metric">
                    <span class="label">Profit:</span>
                    <span class="value" style="color:#4CAF50;">+{profit_pct:.2f}%</span>
                </div>

                <hr>

                <div class="action">
                    <h3>📊 Action Required</h3>
                    <ol>
                        <li><strong>Book {booking_pct}% of position</strong> at current market price</li>
                        <li><strong>Trail stop loss</strong> to protect remaining position</li>
                        <li><strong>Hold remaining {100-booking_pct}%</strong> for next target</li>
                    </ol>

                    <h3>🛡️ Updated Stop Loss</h3>
                    <p>Move stop loss to <strong>₹{target_price*0.98:.2f}</strong> (2% below Target {target_num})</p>
                </div>

                <p style="text-align:center; color:#4CAF50; font-weight:bold; font-size:18px;">
                    Congratulations on your profit! 🎉
                </p>
            </div>

            <div class="footer">
                <p>Generated by Stock Pattern Scanner | {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}</p>
            </div>
        </body>
        </html>
        """

        return self._send_email(subject, body)

    def _send_email(self, subject: str, body: str) -> bool:
        """Send HTML email via SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject

            html_part = MIMEText(body, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
