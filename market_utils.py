"""
Market Utilities
Market hours checking, market condition scoring, and market data utilities
"""

import yfinance as yf
from datetime import datetime, time as dt_time
import pytz
from typing import Tuple, Union
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class MarketUtils:
    """Utilities for market timing and condition analysis"""

    def __init__(self):
        self.ist_tz = pytz.timezone('Asia/Kolkata')
        self.market_open_time = dt_time(9, 15)
        self.market_close_time = dt_time(15, 30)

    def is_market_open(self, return_message: bool = False) -> Union[bool, Tuple[bool, str]]:
        """
        Check if NSE market is currently open

        Market hours: Monday-Friday, 9:15 AM - 3:30 PM IST
        Excludes market holidays (basic check)

        Returns:
            bool or (bool, str): Market open status and optional message
        """
        now = datetime.now(self.ist_tz)

        # Check if weekend
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            if return_message:
                return False, "Market closed (Weekend)"
            return False

        # Check if within market hours
        current_time = now.time()
        is_open = self.market_open_time <= current_time <= self.market_close_time

        if return_message:
            if is_open:
                return True, "Market OPEN"
            else:
                if current_time < self.market_open_time:
                    return False, f"Market opens at {self.market_open_time.strftime('%H:%M')} IST"
                else:
                    return False, "Market closed for the day"

        return is_open

    def get_market_condition_score(self) -> int:
        """
        Calculate market condition score (0-100)

        Scoring components:
        - Nifty trend: +30 points if bullish
        - Sector trend: +25 points if strong (using Bank Nifty as proxy)
        - VIX: +20 points if <15 (low volatility)
        - Market breadth: +15 points if >1.5:1 (advances/declines)
        - FII activity: +10 points if buying (simplified check)

        Returns:
            int: Score from 0-100
        """
        score = 0

        try:
            # 1. Nifty Trend (30 points)
            nifty_score = self._get_nifty_trend_score()
            score += nifty_score
            logger.debug(f"Nifty trend score: {nifty_score}")

            # 2. Sector Trend - Bank Nifty (25 points)
            sector_score = self._get_sector_trend_score()
            score += sector_score
            logger.debug(f"Sector trend score: {sector_score}")

            # 3. VIX Score (20 points)
            vix_score = self._get_vix_score()
            score += vix_score
            logger.debug(f"VIX score: {vix_score}")

            # 4. Market Breadth (15 points) - Simplified
            breadth_score = self._get_market_breadth_score()
            score += breadth_score
            logger.debug(f"Market breadth score: {breadth_score}")

            # 5. FII Activity (10 points) - Simplified using Nifty momentum
            fii_score = self._get_fii_activity_score()
            score += fii_score
            logger.debug(f"FII activity score: {fii_score}")

            logger.info(f"Total market condition score: {score}/100")
            return min(100, score)

        except Exception as e:
            logger.error(f"Error calculating market score: {e}")
            return 50  # Default neutral score

    def _get_nifty_trend_score(self) -> int:
        """
        Calculate Nifty trend score (0-30)

        Checks:
        - Price above 50-day MA: +15 points
        - Price above 200-day MA: +10 points
        - Recent momentum (5-day gain): +5 points
        """
        try:
            nifty = yf.Ticker("^NSEI")
            df = nifty.history(period='1y')

            if df.empty or len(df) < 200:
                return 15  # Neutral

            current_price = df['Close'].iloc[-1]

            score = 0

            # 50-day MA check
            if len(df) >= 50:
                ma50 = df['Close'].tail(50).mean()
                if current_price > ma50:
                    score += 15

            # 200-day MA check
            if len(df) >= 200:
                ma200 = df['Close'].tail(200).mean()
                if current_price > ma200:
                    score += 10

            # Recent momentum (5-day)
            if len(df) >= 5:
                five_day_change = (current_price - df['Close'].iloc[-6]) / df['Close'].iloc[-6] * 100
                if five_day_change > 1:
                    score += 5
                elif five_day_change > 0:
                    score += 3

            return score

        except Exception as e:
            logger.warning(f"Error fetching Nifty data: {e}")
            return 15  # Neutral

    def _get_sector_trend_score(self) -> int:
        """
        Calculate sector trend score using Bank Nifty (0-25)

        Checks:
        - Price above 50-day MA: +15 points
        - Recent momentum: +10 points
        """
        try:
            banknifty = yf.Ticker("^NSEBANK")
            df = banknifty.history(period='6mo')

            if df.empty or len(df) < 50:
                return 12  # Neutral

            current_price = df['Close'].iloc[-1]

            score = 0

            # 50-day MA check
            if len(df) >= 50:
                ma50 = df['Close'].tail(50).mean()
                if current_price > ma50:
                    score += 15

            # Recent momentum (5-day)
            if len(df) >= 5:
                five_day_change = (current_price - df['Close'].iloc[-6]) / df['Close'].iloc[-6] * 100
                if five_day_change > 1:
                    score += 10
                elif five_day_change > 0:
                    score += 5

            return score

        except Exception as e:
            logger.warning(f"Error fetching Bank Nifty data: {e}")
            return 12  # Neutral

    def _get_vix_score(self) -> int:
        """
        Calculate VIX score (0-20)

        VIX (India VIX - Volatility Index):
        - <12: +20 points (very low volatility)
        - 12-15: +15 points (low volatility)
        - 15-20: +10 points (moderate)
        - 20-25: +5 points (elevated)
        - >25: +0 points (high volatility)
        """
        try:
            vix = yf.Ticker("^INDIAVIX")
            df = vix.history(period='5d')

            if df.empty:
                return 10  # Neutral

            current_vix = df['Close'].iloc[-1]

            if current_vix < 12:
                return 20
            elif current_vix < 15:
                return 15
            elif current_vix < 20:
                return 10
            elif current_vix < 25:
                return 5
            else:
                return 0

        except Exception as e:
            logger.warning(f"Error fetching VIX data: {e}")
            return 10  # Neutral

    def _get_market_breadth_score(self) -> int:
        """
        Calculate market breadth score (0-15)

        Simplified using Nifty 50 components momentum
        Compares advances vs declines in major indices
        """
        try:
            # Use Nifty and Bank Nifty as proxies
            nifty = yf.Ticker("^NSEI")
            banknifty = yf.Ticker("^NSEBANK")

            nifty_df = nifty.history(period='5d')
            bank_df = banknifty.history(period='5d')

            if nifty_df.empty or bank_df.empty or len(nifty_df) < 2 or len(bank_df) < 2:
                return 7  # Neutral

            # Check if both rising
            nifty_up = nifty_df['Close'].iloc[-1] > nifty_df['Close'].iloc[-2]
            bank_up = bank_df['Close'].iloc[-1] > bank_df['Close'].iloc[-2]

            if nifty_up and bank_up:
                return 15
            elif nifty_up or bank_up:
                return 10
            else:
                return 3

        except Exception as e:
            logger.warning(f"Error calculating market breadth: {e}")
            return 7  # Neutral

    def _get_fii_activity_score(self) -> int:
        """
        Calculate FII activity score (0-10)

        Simplified: Uses Nifty volume and price momentum as proxy
        - High volume + price up: +10 (likely FII buying)
        - Price up: +5
        - Otherwise: +0
        """
        try:
            nifty = yf.Ticker("^NSEI")
            df = nifty.history(period='1mo')

            if df.empty or len(df) < 20:
                return 5  # Neutral

            recent_volume = df['Volume'].tail(5).mean()
            avg_volume = df['Volume'].tail(20).mean()
            price_change = (df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6] * 100

            if price_change > 1 and recent_volume > avg_volume * 1.2:
                return 10
            elif price_change > 0:
                return 5
            else:
                return 0

        except Exception as e:
            logger.warning(f"Error calculating FII activity: {e}")
            return 5  # Neutral

    def get_market_summary(self) -> dict:
        """
        Get comprehensive market summary

        Returns:
            dict: Market data including Nifty, Bank Nifty, VIX, etc.
        """
        summary = {
            'timestamp': datetime.now(self.ist_tz).strftime('%Y-%m-%d %H:%M:%S IST'),
            'market_open': self.is_market_open(),
            'condition_score': self.get_market_condition_score()
        }

        try:
            # Nifty
            nifty = yf.Ticker("^NSEI")
            nifty_data = nifty.history(period='5d')
            if not nifty_data.empty:
                summary['nifty_price'] = nifty_data['Close'].iloc[-1]
                summary['nifty_change'] = ((nifty_data['Close'].iloc[-1] - nifty_data['Close'].iloc[-2]) /
                                           nifty_data['Close'].iloc[-2] * 100)

            # Bank Nifty
            banknifty = yf.Ticker("^NSEBANK")
            bank_data = banknifty.history(period='5d')
            if not bank_data.empty:
                summary['banknifty_price'] = bank_data['Close'].iloc[-1]
                summary['banknifty_change'] = ((bank_data['Close'].iloc[-1] - bank_data['Close'].iloc[-2]) /
                                                bank_data['Close'].iloc[-2] * 100)

            # VIX
            vix = yf.Ticker("^INDIAVIX")
            vix_data = vix.history(period='5d')
            if not vix_data.empty:
                summary['vix'] = vix_data['Close'].iloc[-1]

        except Exception as e:
            logger.error(f"Error fetching market summary: {e}")

        return summary
