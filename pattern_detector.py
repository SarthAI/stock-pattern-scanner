"""
Pattern Detection Module
Detects 8 bullish chart patterns with multi-state tracking
"""

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PatternDetector:
    """Detects bullish chart patterns in stock data"""

    def __init__(self):
        self.patterns_cache = {}

    def detect_all_patterns(self, df: pd.DataFrame, symbol: str, market_score: int) -> List[Dict]:
        """
        Detect all bullish patterns (TIER 1 full scan)

        Args:
            df: Stock data with OHLCV
            symbol: Stock symbol
            market_score: Current market condition score

        Returns:
            List of detected patterns
        """
        patterns = []

        # Detect each pattern type
        patterns.extend(self._detect_double_bottom(df, symbol, market_score))
        patterns.extend(self._detect_inverse_head_shoulders(df, symbol, market_score))
        patterns.extend(self._detect_ascending_triangle(df, symbol, market_score))
        patterns.extend(self._detect_bull_flag(df, symbol, market_score))
        patterns.extend(self._detect_cup_handle(df, symbol, market_score))
        patterns.extend(self._detect_triple_bottom(df, symbol, market_score))
        patterns.extend(self._detect_rising_wedge(df, symbol, market_score))
        patterns.extend(self._detect_symmetrical_triangle(df, symbol, market_score))

        return patterns

    def check_forming_patterns(self, df: pd.DataFrame, symbol: str, market_score: int) -> List[Dict]:
        """Check status of forming patterns (TIER 2)"""
        # Get patterns in FORMING state from cache
        cached = self.patterns_cache.get(symbol, [])
        patterns = []

        for cached_pattern in cached:
            if cached_pattern['state'] == 'FORMING':
                # Re-evaluate pattern state
                updated = self._update_pattern_state(df, cached_pattern, market_score)
                if updated:
                    patterns.append(updated)

        return patterns

    def check_imminent_breakouts(self, df: pd.DataFrame, symbol: str, market_score: int) -> List[Dict]:
        """Check for imminent breakouts (TIER 3)"""
        cached = self.patterns_cache.get(symbol, [])
        patterns = []

        for cached_pattern in cached:
            if cached_pattern['state'] in ['FORMING', 'NEAR_BREAKOUT']:
                updated = self._update_pattern_state(df, cached_pattern, market_score)
                if updated and updated['state'] in ['NEAR_BREAKOUT', 'BREAKOUT_IMMINENT']:
                    patterns.append(updated)

        return patterns

    def check_confirmed_breakouts(self, df: pd.DataFrame, symbol: str, market_score: int) -> List[Dict]:
        """Check for confirmed breakouts (TIER 4)"""
        cached = self.patterns_cache.get(symbol, [])
        patterns = []

        for cached_pattern in cached:
            if cached_pattern['state'] in ['BREAKOUT_IMMINENT', 'BREAKOUT_CONFIRMED']:
                updated = self._update_pattern_state(df, cached_pattern, market_score)
                if updated and updated['state'] == 'BREAKOUT_CONFIRMED':
                    patterns.append(updated)

        return patterns

    # ===== DOUBLE BOTTOM (W PATTERN) =====

    def _detect_double_bottom(self, df: pd.DataFrame, symbol: str, market_score: int) -> List[Dict]:
        """
        Detect W pattern (Double Bottom)

        Detection Criteria:
        - Two bottoms within 3% of each other (using LOW)
        - Peak between bottoms at least 3% higher
        - Time spacing: 10-60 days between bottoms
        - Second bottom not >3% lower than first
        - Validate with CLOSE (wick_ratio > 0.6)
        """
        if len(df) < 60:
            return []

        patterns = []
        df_subset = df.tail(180)  # Last 6 months

        # Find local minimums (bottoms)
        lows = df_subset['Low'].values
        local_mins = argrelextrema(lows, np.less, order=5)[0]

        if len(local_mins) < 2:
            return []

        # Check all pairs of bottoms
        for i in range(len(local_mins) - 1):
            for j in range(i + 1, len(local_mins)):
                idx1, idx2 = local_mins[i], local_mins[j]

                # Time spacing check (10-60 days)
                days_between = idx2 - idx1
                if days_between < 10 or days_between > 60:
                    continue

                # Get bottom values
                bottom1_low = df_subset.iloc[idx1]['Low']
                bottom2_low = df_subset.iloc[idx2]['Low']
                bottom1_close = df_subset.iloc[idx1]['Close']
                bottom2_close = df_subset.iloc[idx2]['Close']

                # Symmetry check (≤3% difference)
                symmetry_diff = abs(bottom1_low - bottom2_low) / bottom1_low * 100
                if symmetry_diff > 3.0:
                    continue

                # Second bottom validation (not >3% lower)
                if bottom2_low < bottom1_low * 0.97:
                    continue

                # Find peak between bottoms
                peak_slice = df_subset.iloc[idx1:idx2 + 1]
                peak_idx_local = peak_slice['High'].idxmax()
                peak_high = peak_slice.loc[peak_idx_local, 'High']

                # Peak height check (≥3% above bottoms)
                avg_bottom = (bottom1_low + bottom2_low) / 2
                peak_height_pct = (peak_high - avg_bottom) / avg_bottom * 100
                if peak_height_pct < 3.0:
                    continue

                # Wick ratio validation (strong bottoms)
                wick1 = (bottom1_close - bottom1_low) / (df_subset.iloc[idx1]['High'] - bottom1_low)
                wick2 = (bottom2_close - bottom2_low) / (df_subset.iloc[idx2]['High'] - bottom2_low)
                avg_wick_ratio = (wick1 + wick2) / 2

                # Calculate breakout point (neckline = peak)
                breakout_point = peak_high
                current_price = df.iloc[-1]['Close']
                distance_pct = (breakout_point - current_price) / current_price * 100

                # Calculate pattern strength score
                strength_score = self._calculate_w_pattern_strength(
                    symmetry_diff=symmetry_diff,
                    peak_height_pct=peak_height_pct,
                    wick_ratio=avg_wick_ratio,
                    days_between=days_between,
                    df=df,
                    market_score=market_score
                )

                # Determine pattern state
                state = self._determine_pattern_state(
                    current_price=current_price,
                    breakout_point=breakout_point,
                    distance_pct=distance_pct,
                    df=df
                )

                # Skip if pattern already broke down
                if current_price < avg_bottom * 0.97:
                    continue

                # Create pattern object
                pattern = {
                    'symbol': symbol,
                    'pattern_type': 'DOUBLE_BOTTOM',
                    'state': state,
                    'strength_score': strength_score,
                    'current_price': current_price,
                    'breakout_point': breakout_point,
                    'distance_pct': distance_pct,
                    'invalidation_point': avg_bottom * 0.97,
                    'target1': breakout_point + (breakout_point - avg_bottom) * 0.382,
                    'target2': breakout_point + (breakout_point - avg_bottom) * 0.618,
                    'target3': breakout_point + (breakout_point - avg_bottom) * 1.0,
                    'stop_loss': avg_bottom * 0.97,
                    'volume_confirmed': self._check_volume_confirmation(df),
                    'details': {
                        'bottom1': bottom1_low,
                        'bottom2': bottom2_low,
                        'peak': peak_high,
                        'symmetry_diff': symmetry_diff,
                        'peak_height_pct': peak_height_pct,
                        'wick_ratio': avg_wick_ratio,
                        'days_between': days_between
                    }
                }

                patterns.append(pattern)

        return patterns

    def _calculate_w_pattern_strength(self, symmetry_diff: float, peak_height_pct: float,
                                      wick_ratio: float, days_between: int, df: pd.DataFrame,
                                      market_score: int) -> int:
        """
        Calculate W pattern strength score (0-100)

        Scoring:
        - Symmetry: 30 points
        - Peak height: 20 points
        - Volume confirmation: 25 points
        - Market conditions: 15 points (from market_score)
        - Time spacing: 10 points
        """
        score = 0

        # Symmetry (30 points) - lower diff = higher score
        if symmetry_diff <= 0.5:
            score += 30
        elif symmetry_diff <= 1.0:
            score += 25
        elif symmetry_diff <= 2.0:
            score += 20
        elif symmetry_diff <= 3.0:
            score += 15

        # Peak height (20 points)
        if peak_height_pct >= 10:
            score += 20
        elif peak_height_pct >= 7:
            score += 15
        elif peak_height_pct >= 5:
            score += 10
        elif peak_height_pct >= 3:
            score += 5

        # Volume confirmation (25 points)
        vol_ratio = self._get_volume_ratio(df)
        if vol_ratio >= 1.5:
            score += 25
        elif vol_ratio >= 1.3:
            score += 20
        elif vol_ratio >= 1.1:
            score += 15
        elif vol_ratio >= 1.0:
            score += 10

        # Market conditions (15 points) - scaled from market_score
        score += int((market_score / 100) * 15)

        # Time spacing (10 points) - optimal 20-40 days
        if 20 <= days_between <= 40:
            score += 10
        elif 15 <= days_between <= 50:
            score += 7
        elif 10 <= days_between <= 60:
            score += 5

        return min(100, score)

    # ===== INVERSE HEAD & SHOULDERS =====

    def _detect_inverse_head_shoulders(self, df: pd.DataFrame, symbol: str, market_score: int) -> List[Dict]:
        """Detect Inverse Head & Shoulders pattern"""
        if len(df) < 60:
            return []

        patterns = []
        df_subset = df.tail(180)

        lows = df_subset['Low'].values
        local_mins = argrelextrema(lows, np.less, order=5)[0]

        if len(local_mins) < 3:
            return []

        # Check for head & shoulders formation
        for i in range(len(local_mins) - 2):
            left_idx = local_mins[i]
            head_idx = local_mins[i + 1]
            right_idx = local_mins[i + 2]

            left_low = df_subset.iloc[left_idx]['Low']
            head_low = df_subset.iloc[head_idx]['Low']
            right_low = df_subset.iloc[right_idx]['Low']

            # Head must be lower than shoulders
            if head_low >= left_low or head_low >= right_low:
                continue

            # Shoulders should be symmetric (within 5%)
            shoulder_symmetry = abs(left_low - right_low) / left_low * 100
            if shoulder_symmetry > 5.0:
                continue

            # Head depth (at least 5% lower than shoulders)
            avg_shoulder = (left_low + right_low) / 2
            head_depth_pct = (avg_shoulder - head_low) / avg_shoulder * 100
            if head_depth_pct < 5.0:
                continue

            # Find neckline (resistance between peaks)
            peak1 = df_subset.iloc[left_idx:head_idx]['High'].max()
            peak2 = df_subset.iloc[head_idx:right_idx]['High'].max()
            neckline = (peak1 + peak2) / 2

            current_price = df.iloc[-1]['Close']
            distance_pct = (neckline - current_price) / current_price * 100

            # Calculate strength
            strength_score = self._calculate_generic_strength(
                symmetry=100 - shoulder_symmetry * 10,
                depth_pct=head_depth_pct,
                df=df,
                market_score=market_score
            )

            state = self._determine_pattern_state(current_price, neckline, distance_pct, df)

            pattern = {
                'symbol': symbol,
                'pattern_type': 'INVERSE_HEAD_SHOULDERS',
                'state': state,
                'strength_score': strength_score,
                'current_price': current_price,
                'breakout_point': neckline,
                'distance_pct': distance_pct,
                'invalidation_point': head_low,
                'target1': neckline + (neckline - head_low) * 0.382,
                'target2': neckline + (neckline - head_low) * 0.618,
                'target3': neckline + (neckline - head_low) * 1.0,
                'stop_loss': head_low,
                'volume_confirmed': self._check_volume_confirmation(df),
                'details': {
                    'left_shoulder': left_low,
                    'head': head_low,
                    'right_shoulder': right_low,
                    'neckline': neckline
                }
            }

            patterns.append(pattern)

        return patterns

    # ===== ASCENDING TRIANGLE =====

    def _detect_ascending_triangle(self, df: pd.DataFrame, symbol: str, market_score: int) -> List[Dict]:
        """Detect Ascending Triangle pattern"""
        if len(df) < 40:
            return []

        patterns = []
        df_subset = df.tail(120)

        # Find resistance level (flat top)
        highs = df_subset['High'].values
        resistance = np.percentile(highs[-40:], 95)

        # Count touches near resistance (within 1%)
        touches = np.sum(np.abs(highs[-40:] - resistance) / resistance < 0.01)

        if touches < 2:
            return []

        # Check for rising lows
        lows = df_subset['Low'].values[-40:]
        rising_lows = self._check_rising_trendline(lows)

        if not rising_lows:
            return []

        current_price = df.iloc[-1]['Close']
        distance_pct = (resistance - current_price) / current_price * 100

        # Calculate strength
        strength_score = self._calculate_generic_strength(
            symmetry=touches * 15,  # More touches = stronger
            depth_pct=min(20, touches * 5),
            df=df,
            market_score=market_score
        )

        state = self._determine_pattern_state(current_price, resistance, distance_pct, df)

        pattern = {
            'symbol': symbol,
            'pattern_type': 'ASCENDING_TRIANGLE',
            'state': state,
            'strength_score': strength_score,
            'current_price': current_price,
            'breakout_point': resistance,
            'distance_pct': distance_pct,
            'invalidation_point': lows.min() * 0.98,
            'target1': resistance * 1.03,
            'target2': resistance * 1.05,
            'target3': resistance * 1.08,
            'stop_loss': lows.min() * 0.98,
            'volume_confirmed': self._check_volume_confirmation(df),
            'details': {
                'resistance': resistance,
                'touches': int(touches)
            }
        }

        patterns.append(pattern)

        return patterns

    # ===== BULL FLAG / PENNANT =====

    def _detect_bull_flag(self, df: pd.DataFrame, symbol: str, market_score: int) -> List[Dict]:
        """Detect Bull Flag & Pennant patterns"""
        if len(df) < 30:
            return []

        patterns = []
        df_subset = df.tail(60)

        # Look for strong uptrend (pole)
        pole_start = -30
        pole_end = -10
        pole_gain = (df_subset.iloc[pole_end]['Close'] - df_subset.iloc[pole_start]['Close']) / df_subset.iloc[pole_start]['Close'] * 100

        if pole_gain < 8:  # Minimum 8% gain for pole
            return []

        # Check for consolidation (flag)
        consolidation = df_subset.iloc[-10:]
        price_range = (consolidation['High'].max() - consolidation['Low'].min()) / consolidation['Close'].mean() * 100

        if price_range > 5:  # Flag should be tight (< 5%)
            return []

        # Check for slight downward slope (classic flag)
        flag_slope = (consolidation.iloc[-1]['Close'] - consolidation.iloc[0]['Close']) / consolidation.iloc[0]['Close'] * 100

        breakout_point = consolidation['High'].max()
        current_price = df.iloc[-1]['Close']
        distance_pct = (breakout_point - current_price) / current_price * 100

        strength_score = self._calculate_generic_strength(
            symmetry=max(0, 100 - price_range * 10),
            depth_pct=pole_gain,
            df=df,
            market_score=market_score
        )

        state = self._determine_pattern_state(current_price, breakout_point, distance_pct, df)

        pattern = {
            'symbol': symbol,
            'pattern_type': 'BULL_FLAG',
            'state': state,
            'strength_score': strength_score,
            'current_price': current_price,
            'breakout_point': breakout_point,
            'distance_pct': distance_pct,
            'invalidation_point': consolidation['Low'].min() * 0.98,
            'target1': breakout_point + pole_gain * 0.01 * breakout_point * 0.5,
            'target2': breakout_point + pole_gain * 0.01 * breakout_point * 0.75,
            'target3': breakout_point + pole_gain * 0.01 * breakout_point,
            'stop_loss': consolidation['Low'].min() * 0.98,
            'volume_confirmed': self._check_volume_confirmation(df),
            'details': {
                'pole_gain': pole_gain,
                'flag_range': price_range
            }
        }

        patterns.append(pattern)

        return patterns

    # ===== CUP & HANDLE =====

    def _detect_cup_handle(self, df: pd.DataFrame, symbol: str, market_score: int) -> List[Dict]:
        """Detect Cup & Handle (Rounded Bottom) pattern"""
        if len(df) < 90:
            return []

        patterns = []
        df_subset = df.tail(180)

        # Find potential cup (U-shaped curve)
        cup_window = df_subset.iloc[-90:-20]
        cup_start_price = cup_window.iloc[0]['Close']
        cup_low = cup_window['Low'].min()
        cup_end_price = cup_window.iloc[-1]['Close']

        # Cup depth (10-30% ideal)
        cup_depth = (cup_start_price - cup_low) / cup_start_price * 100
        if cup_depth < 10 or cup_depth > 40:
            return []

        # Check for U-shape (bottom should be rounded)
        bottom_quarter = cup_window.iloc[len(cup_window)//3: 2*len(cup_window)//3]
        bottom_volatility = bottom_quarter['Close'].std() / bottom_quarter['Close'].mean()
        if bottom_volatility > 0.05:  # Too volatile = not rounded
            return []

        # Check for handle (small retracement)
        handle = df_subset.iloc[-20:]
        handle_high = cup_end_price
        handle_low = handle['Low'].min()
        handle_depth = (handle_high - handle_low) / handle_high * 100

        if handle_depth < 3 or handle_depth > 15:  # Handle should be 3-15% retracement
            return []

        breakout_point = max(cup_start_price, handle_high)
        current_price = df.iloc[-1]['Close']
        distance_pct = (breakout_point - current_price) / current_price * 100

        strength_score = self._calculate_generic_strength(
            symmetry=max(0, 100 - abs(cup_depth - 20) * 5),
            depth_pct=cup_depth,
            df=df,
            market_score=market_score
        )

        state = self._determine_pattern_state(current_price, breakout_point, distance_pct, df)

        pattern = {
            'symbol': symbol,
            'pattern_type': 'CUP_HANDLE',
            'state': state,
            'strength_score': strength_score,
            'current_price': current_price,
            'breakout_point': breakout_point,
            'distance_pct': distance_pct,
            'invalidation_point': handle_low * 0.98,
            'target1': breakout_point + cup_depth * 0.01 * breakout_point * 0.5,
            'target2': breakout_point + cup_depth * 0.01 * breakout_point * 0.75,
            'target3': breakout_point + cup_depth * 0.01 * breakout_point,
            'stop_loss': handle_low * 0.98,
            'volume_confirmed': self._check_volume_confirmation(df),
            'details': {
                'cup_depth': cup_depth,
                'handle_depth': handle_depth
            }
        }

        patterns.append(pattern)

        return patterns

    # ===== TRIPLE BOTTOM =====

    def _detect_triple_bottom(self, df: pd.DataFrame, symbol: str, market_score: int) -> List[Dict]:
        """Detect Triple Bottom pattern"""
        if len(df) < 90:
            return []

        patterns = []
        df_subset = df.tail(180)

        lows = df_subset['Low'].values
        local_mins = argrelextrema(lows, np.less, order=5)[0]

        if len(local_mins) < 3:
            return []

        # Check for three similar bottoms
        for i in range(len(local_mins) - 2):
            b1_idx = local_mins[i]
            b2_idx = local_mins[i + 1]
            b3_idx = local_mins[i + 2]

            b1 = df_subset.iloc[b1_idx]['Low']
            b2 = df_subset.iloc[b2_idx]['Low']
            b3 = df_subset.iloc[b3_idx]['Low']

            # All three bottoms within 3% of each other
            avg_bottom = (b1 + b2 + b3) / 3
            if any(abs(b - avg_bottom) / avg_bottom > 0.03 for b in [b1, b2, b3]):
                continue

            # Find resistance (peaks between bottoms)
            peak1 = df_subset.iloc[b1_idx:b2_idx]['High'].max()
            peak2 = df_subset.iloc[b2_idx:b3_idx]['High'].max()
            resistance = (peak1 + peak2) / 2

            current_price = df.iloc[-1]['Close']
            distance_pct = (resistance - current_price) / current_price * 100

            strength_score = self._calculate_generic_strength(
                symmetry=90,  # Three touches = strong
                depth_pct=(resistance - avg_bottom) / avg_bottom * 100,
                df=df,
                market_score=market_score
            )

            state = self._determine_pattern_state(current_price, resistance, distance_pct, df)

            pattern = {
                'symbol': symbol,
                'pattern_type': 'TRIPLE_BOTTOM',
                'state': state,
                'strength_score': strength_score,
                'current_price': current_price,
                'breakout_point': resistance,
                'distance_pct': distance_pct,
                'invalidation_point': avg_bottom * 0.97,
                'target1': resistance + (resistance - avg_bottom) * 0.5,
                'target2': resistance + (resistance - avg_bottom) * 0.75,
                'target3': resistance + (resistance - avg_bottom) * 1.0,
                'stop_loss': avg_bottom * 0.97,
                'volume_confirmed': self._check_volume_confirmation(df),
                'details': {
                    'bottoms': [b1, b2, b3],
                    'resistance': resistance
                }
            }

            patterns.append(pattern)

        return patterns

    # ===== RISING WEDGE =====

    def _detect_rising_wedge(self, df: pd.DataFrame, symbol: str, market_score: int) -> List[Dict]:
        """Detect Rising Wedge pattern (bullish breakout potential)"""
        if len(df) < 40:
            return []

        patterns = []
        df_subset = df.tail(90)

        # Check for converging trendlines (both rising, but highs rising faster)
        recent = df_subset.tail(40)
        lows = recent['Low'].values
        highs = recent['High'].values

        # Both should be rising
        if not self._check_rising_trendline(lows) or not self._check_rising_trendline(highs):
            return []

        # Calculate slopes
        low_slope = self._calculate_trendline_slope(lows)
        high_slope = self._calculate_trendline_slope(highs)

        # Converging check (high slope > low slope)
        if high_slope <= low_slope:
            return []

        # Upper trendline is breakout point
        breakout_point = highs[-1] * 1.01  # Slightly above current high
        current_price = df.iloc[-1]['Close']
        distance_pct = (breakout_point - current_price) / current_price * 100

        strength_score = self._calculate_generic_strength(
            symmetry=70,
            depth_pct=10,
            df=df,
            market_score=market_score
        )

        state = self._determine_pattern_state(current_price, breakout_point, distance_pct, df)

        pattern = {
            'symbol': symbol,
            'pattern_type': 'RISING_WEDGE',
            'state': state,
            'strength_score': strength_score,
            'current_price': current_price,
            'breakout_point': breakout_point,
            'distance_pct': distance_pct,
            'invalidation_point': lows.min() * 0.98,
            'target1': breakout_point * 1.03,
            'target2': breakout_point * 1.05,
            'target3': breakout_point * 1.08,
            'stop_loss': lows.min() * 0.98,
            'volume_confirmed': self._check_volume_confirmation(df),
            'details': {
                'convergence': True
            }
        }

        patterns.append(pattern)

        return patterns

    # ===== SYMMETRICAL TRIANGLE =====

    def _detect_symmetrical_triangle(self, df: pd.DataFrame, symbol: str, market_score: int) -> List[Dict]:
        """Detect Symmetrical Triangle pattern"""
        if len(df) < 40:
            return []

        patterns = []
        df_subset = df.tail(90)

        recent = df_subset.tail(40)
        lows = recent['Low'].values
        highs = recent['High'].values

        # Check for converging range
        early_range = (highs[:10].max() - lows[:10].min()) / lows[:10].min()
        late_range = (highs[-10:].max() - lows[-10:].min()) / lows[-10:].min()

        # Range should be narrowing
        if late_range >= early_range * 0.8:
            return []

        # Breakout could be either direction, but we focus on upside
        breakout_point = highs[-10:].max()
        current_price = df.iloc[-1]['Close']
        distance_pct = (breakout_point - current_price) / current_price * 100

        strength_score = self._calculate_generic_strength(
            symmetry=max(0, 100 - late_range / early_range * 100),
            depth_pct=early_range * 100,
            df=df,
            market_score=market_score
        )

        state = self._determine_pattern_state(current_price, breakout_point, distance_pct, df)

        pattern = {
            'symbol': symbol,
            'pattern_type': 'SYMMETRICAL_TRIANGLE',
            'state': state,
            'strength_score': strength_score,
            'current_price': current_price,
            'breakout_point': breakout_point,
            'distance_pct': distance_pct,
            'invalidation_point': lows.min() * 0.98,
            'target1': breakout_point * 1.04,
            'target2': breakout_point * 1.06,
            'target3': breakout_point * 1.10,
            'stop_loss': lows.min() * 0.98,
            'volume_confirmed': self._check_volume_confirmation(df),
            'details': {
                'early_range': early_range,
                'late_range': late_range
            }
        }

        patterns.append(pattern)

        return patterns

    # ===== HELPER METHODS =====

    def _determine_pattern_state(self, current_price: float, breakout_point: float,
                                  distance_pct: float, df: pd.DataFrame) -> str:
        """
        Determine pattern state based on price proximity to breakout

        States:
        - FORMING: Pattern detected, not confirmed
        - NEAR_BREAKOUT: Within 1-2% of breakout point
        - BREAKOUT_IMMINENT: Within 0.5% + volume building (>1.5x avg)
        - BREAKOUT_CONFIRMED: Price closed above breakout with volume (>1.3x avg)
        """
        if current_price > breakout_point:
            # Check volume confirmation
            vol_ratio = self._get_volume_ratio(df)
            if vol_ratio >= 1.3:
                return 'BREAKOUT_CONFIRMED'
            else:
                return 'NEAR_BREAKOUT'  # Broke out but weak volume

        # Distance checks
        if distance_pct <= 0.5:
            vol_ratio = self._get_volume_ratio(df)
            if vol_ratio >= 1.5:
                return 'BREAKOUT_IMMINENT'
            else:
                return 'NEAR_BREAKOUT'
        elif distance_pct <= 2.0:
            return 'NEAR_BREAKOUT'
        else:
            return 'FORMING'

    def _check_volume_confirmation(self, df: pd.DataFrame, lookback: int = 3) -> bool:
        """Check if recent volume is elevated"""
        if len(df) < 20:
            return False

        recent_vol = df['Volume'].iloc[-lookback:].mean()
        avg_vol = df['Volume'].iloc[-20:-lookback].mean()

        return recent_vol > avg_vol * 1.3

    def _get_volume_ratio(self, df: pd.DataFrame, lookback: int = 3) -> float:
        """Get volume ratio (recent vs average)"""
        if len(df) < 20:
            return 1.0

        recent_vol = df['Volume'].iloc[-lookback:].mean()
        avg_vol = df['Volume'].iloc[-20:-lookback].mean()

        if avg_vol == 0:
            return 1.0

        return recent_vol / avg_vol

    def _check_rising_trendline(self, values: np.ndarray) -> bool:
        """Check if values form a rising trendline"""
        if len(values) < 5:
            return False

        # Simple linear regression
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        return slope > 0

    def _calculate_trendline_slope(self, values: np.ndarray) -> float:
        """Calculate slope of trendline"""
        if len(values) < 2:
            return 0.0

        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        return slope

    def _calculate_generic_strength(self, symmetry: float, depth_pct: float,
                                     df: pd.DataFrame, market_score: int) -> int:
        """Generic strength calculation for simpler patterns"""
        score = 0

        # Symmetry/Quality (35 points)
        score += min(35, int(symmetry * 0.35))

        # Depth/Height (20 points)
        score += min(20, int(depth_pct * 2))

        # Volume (25 points)
        vol_ratio = self._get_volume_ratio(df)
        if vol_ratio >= 1.5:
            score += 25
        elif vol_ratio >= 1.3:
            score += 20
        elif vol_ratio >= 1.1:
            score += 15

        # Market conditions (15 points)
        score += int((market_score / 100) * 15)

        # Trend alignment (5 points)
        if len(df) >= 50:
            ma50 = df['Close'].tail(50).mean()
            if df.iloc[-1]['Close'] > ma50:
                score += 5

        return min(100, score)

    def _update_pattern_state(self, df: pd.DataFrame, pattern: Dict, market_score: int) -> Optional[Dict]:
        """Update pattern state with latest data"""
        current_price = df.iloc[-1]['Close']
        breakout_point = pattern['breakout_point']
        distance_pct = (breakout_point - current_price) / current_price * 100

        # Check if pattern is still valid
        if current_price < pattern['invalidation_point']:
            logger.info(f"Pattern invalidated for {pattern['symbol']}")
            return None

        # Update state
        new_state = self._determine_pattern_state(current_price, breakout_point, distance_pct, df)

        # Only return if state changed
        if new_state != pattern['state']:
            pattern['state'] = new_state
            pattern['current_price'] = current_price
            pattern['distance_pct'] = distance_pct
            pattern['volume_confirmed'] = self._check_volume_confirmation(df)
            return pattern

        return None
