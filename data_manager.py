"""
Data Manager
Handles stock data fetching, pattern storage, and database operations
"""

import yfinance as yf
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json
import time

logger = logging.getLogger(__name__)


class DataManager:
    """Manages stock data and pattern persistence"""

    def __init__(self, db_path: str = 'stock_patterns.db'):
        self.db_path = db_path
        self._init_database()
        self._cache = {}
        self._cache_expiry = {}

    def _init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    state TEXT NOT NULL,
                    strength_score INTEGER,
                    current_price REAL,
                    breakout_point REAL,
                    distance_pct REAL,
                    invalidation_point REAL,
                    target1 REAL,
                    target2 REAL,
                    target3 REAL,
                    stop_loss REAL,
                    volume_confirmed INTEGER,
                    details TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active INTEGER DEFAULT 1
                )
            ''')

            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id INTEGER,
                    symbol TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    price REAL,
                    strength_score INTEGER,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pattern_id) REFERENCES patterns(id)
                )
            ''')

            # Pattern statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pattern_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id INTEGER,
                    symbol TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    entry_price REAL,
                    exit_price REAL,
                    target_hit INTEGER,
                    profit_loss_pct REAL,
                    success INTEGER,
                    closed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pattern_id) REFERENCES patterns(id)
                )
            ''')

            # Config table for stock list and settings persistence
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_symbol ON patterns(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_state ON patterns(state)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_active ON patterns(active)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts(symbol)')

            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def fetch_stock_data(self, symbol: str, period: str = '1y',
                        use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        Fetch stock data from yfinance with caching and error handling

        Args:
            symbol: Stock symbol (with .NS suffix for NSE)
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            use_cache: Whether to use cached data

        Returns:
            DataFrame with OHLCV data or None if fetch fails
        """
        cache_key = f"{symbol}_{period}"

        # Check cache
        if use_cache and cache_key in self._cache:
            expiry = self._cache_expiry.get(cache_key)
            if expiry and datetime.now() < expiry:
                logger.debug(f"Using cached data for {symbol}")
                return self._cache[cache_key]

        try:
            logger.debug(f"Fetching data for {symbol} (period={period})")
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)

            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return None

            # Cache the data (expires in 5 minutes)
            self._cache[cache_key] = df
            self._cache_expiry[cache_key] = datetime.now() + timedelta(minutes=5)

            logger.debug(f"Fetched {len(df)} rows for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def save_pattern(self, pattern: Dict) -> int:
        """
        Save or update pattern in database

        Returns:
            pattern_id: Database ID of the pattern
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if pattern already exists (same symbol, pattern_type, and still active)
            cursor.execute('''
                SELECT id, state FROM patterns
                WHERE symbol = ? AND pattern_type = ? AND active = 1
                ORDER BY detected_at DESC LIMIT 1
            ''', (pattern['symbol'], pattern['pattern_type']))

            existing = cursor.fetchone()

            if existing:
                pattern_id, old_state = existing

                # Update existing pattern
                cursor.execute('''
                    UPDATE patterns SET
                        state = ?,
                        strength_score = ?,
                        current_price = ?,
                        breakout_point = ?,
                        distance_pct = ?,
                        volume_confirmed = ?,
                        details = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    pattern['state'],
                    pattern['strength_score'],
                    pattern['current_price'],
                    pattern['breakout_point'],
                    pattern['distance_pct'],
                    1 if pattern['volume_confirmed'] else 0,
                    json.dumps(pattern.get('details', {})),
                    pattern_id
                ))

                logger.info(f"Updated pattern {pattern_id} for {pattern['symbol']}")

            else:
                # Insert new pattern
                cursor.execute('''
                    INSERT INTO patterns (
                        symbol, pattern_type, state, strength_score,
                        current_price, breakout_point, distance_pct,
                        invalidation_point, target1, target2, target3,
                        stop_loss, volume_confirmed, details
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern['symbol'],
                    pattern['pattern_type'],
                    pattern['state'],
                    pattern['strength_score'],
                    pattern['current_price'],
                    pattern['breakout_point'],
                    pattern['distance_pct'],
                    pattern['invalidation_point'],
                    pattern['target1'],
                    pattern['target2'],
                    pattern['target3'],
                    pattern['stop_loss'],
                    1 if pattern['volume_confirmed'] else 0,
                    json.dumps(pattern.get('details', {}))
                ))

                pattern_id = cursor.lastrowid
                logger.info(f"Saved new pattern {pattern_id} for {pattern['symbol']}")

            conn.commit()
            conn.close()

            return pattern_id

        except Exception as e:
            logger.error(f"Error saving pattern: {e}")
            return -1

    def save_alert(self, pattern_id: int, symbol: str, pattern_type: str,
                   alert_type: str, price: float, strength_score: int,
                   message: str = "") -> bool:
        """Save alert to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO alerts (
                    pattern_id, symbol, pattern_type, alert_type,
                    price, strength_score, message
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (pattern_id, symbol, pattern_type, alert_type, price, strength_score, message))

            conn.commit()
            conn.close()

            logger.info(f"Saved alert: {alert_type} for {symbol}")
            return True

        except Exception as e:
            logger.error(f"Error saving alert: {e}")
            return False

    def get_active_patterns(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """
        Get all active patterns

        Args:
            symbol: Optional filter by symbol

        Returns:
            DataFrame with active patterns
        """
        try:
            conn = sqlite3.connect(self.db_path)

            query = '''
                SELECT
                    symbol, pattern_type, state, strength_score,
                    current_price, breakout_point, distance_pct,
                    target1, target2, target3, stop_loss,
                    detected_at, updated_at
                FROM patterns
                WHERE active = 1
            '''

            if symbol:
                query += f" AND symbol = '{symbol}'"

            query += " ORDER BY updated_at DESC"

            df = pd.read_sql_query(query, conn)
            conn.close()

            return df

        except Exception as e:
            logger.error(f"Error fetching active patterns: {e}")
            return pd.DataFrame()

    def get_recent_alerts(self, limit: int = 50) -> pd.DataFrame:
        """Get recent alerts"""
        try:
            conn = sqlite3.connect(self.db_path)

            query = f'''
                SELECT
                    symbol, pattern_type, alert_type, price,
                    strength_score, message, timestamp
                FROM alerts
                ORDER BY timestamp DESC
                LIMIT {limit}
            '''

            df = pd.read_sql_query(query, conn)
            conn.close()

            return df

        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return pd.DataFrame()

    def get_pattern_statistics(self) -> Dict:
        """
        Get pattern detection statistics

        Returns:
            dict: Statistics including success rate, pattern distribution, etc.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            stats = {}

            # Total patterns detected
            cursor.execute('SELECT COUNT(*) FROM patterns')
            stats['total_patterns'] = cursor.fetchone()[0]

            # Confirmed breakouts
            cursor.execute('SELECT COUNT(*) FROM patterns WHERE state = "BREAKOUT_CONFIRMED"')
            stats['confirmed_breakouts'] = cursor.fetchone()[0]

            # Pattern distribution
            cursor.execute('''
                SELECT pattern_type, COUNT(*) as count
                FROM patterns
                WHERE active = 1
                GROUP BY pattern_type
            ''')
            stats['pattern_distribution'] = dict(cursor.fetchall())

            # Average strength score
            cursor.execute('SELECT AVG(strength_score) FROM patterns WHERE active = 1')
            result = cursor.fetchone()[0]
            stats['avg_strength'] = result if result else 0

            # Success rate (from pattern_stats table)
            cursor.execute('SELECT COUNT(*) FROM pattern_stats WHERE success = 1')
            successful = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM pattern_stats')
            total_closed = cursor.fetchone()[0]

            if total_closed > 0:
                stats['success_rate'] = (successful / total_closed) * 100
            else:
                stats['success_rate'] = 0

            conn.close()

            return stats

        except Exception as e:
            logger.error(f"Error fetching statistics: {e}")
            return {}

    def invalidate_pattern(self, pattern_id: int) -> bool:
        """Mark pattern as inactive (invalidated)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE patterns SET active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (pattern_id,))

            conn.commit()
            conn.close()

            logger.info(f"Invalidated pattern {pattern_id}")
            return True

        except Exception as e:
            logger.error(f"Error invalidating pattern: {e}")
            return False

    def close_pattern(self, pattern_id: int, exit_price: float, target_hit: int = 0) -> bool:
        """
        Close a pattern and record statistics

        Args:
            pattern_id: Pattern ID
            exit_price: Exit price
            target_hit: Which target was hit (0-3)

        Returns:
            bool: Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get pattern details
            cursor.execute('''
                SELECT symbol, pattern_type, current_price, target3
                FROM patterns WHERE id = ?
            ''', (pattern_id,))

            pattern = cursor.fetchone()
            if not pattern:
                logger.warning(f"Pattern {pattern_id} not found")
                return False

            symbol, pattern_type, entry_price, target3 = pattern

            # Calculate profit/loss
            profit_loss_pct = ((exit_price - entry_price) / entry_price) * 100
            success = 1 if profit_loss_pct > 0 else 0

            # Save statistics
            cursor.execute('''
                INSERT INTO pattern_stats (
                    pattern_id, symbol, pattern_type, entry_price,
                    exit_price, target_hit, profit_loss_pct, success
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (pattern_id, symbol, pattern_type, entry_price,
                  exit_price, target_hit, profit_loss_pct, success))

            # Mark pattern as inactive
            cursor.execute('UPDATE patterns SET active = 0 WHERE id = ?', (pattern_id,))

            conn.commit()
            conn.close()

            logger.info(f"Closed pattern {pattern_id}: {profit_loss_pct:.2f}% P/L")
            return True

        except Exception as e:
            logger.error(f"Error closing pattern: {e}")
            return False

    def cleanup_old_data(self, days: int = 30):
        """
        Clean up old inactive patterns

        Args:
            days: Delete patterns inactive for more than this many days
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_date = datetime.now() - timedelta(days=days)

            cursor.execute('''
                DELETE FROM patterns
                WHERE active = 0 AND updated_at < ?
            ''', (cutoff_date,))

            deleted = cursor.rowcount

            conn.commit()
            conn.close()

            logger.info(f"Cleaned up {deleted} old patterns")

        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

    def get_stock_list_from_file(self, file_path: str) -> List[str]:
        """
        Load stock list from text file

        Args:
            file_path: Path to text file with stock symbols (one per line)

        Returns:
            List of stock symbols
        """
        try:
            with open(file_path, 'r') as f:
                stocks = [line.strip().upper() for line in f if line.strip()]

            logger.info(f"Loaded {len(stocks)} stocks from {file_path}")
            return stocks

        except Exception as e:
            logger.error(f"Error loading stock list: {e}")
            return []

    # ===== CONFIGURATION PERSISTENCE METHODS =====

    def save_stock_list(self, stocks: List[str]) -> bool:
        """
        Save stock list to database for persistence

        Args:
            stocks: List of stock symbols

        Returns:
            bool: Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Convert list to comma-separated string
            stock_string = ','.join(stocks)

            # Insert or update config
            cursor.execute('''
                INSERT OR REPLACE INTO config (key, value, updated_at)
                VALUES ('stock_list', ?, CURRENT_TIMESTAMP)
            ''', (stock_string,))

            conn.commit()
            conn.close()

            logger.info(f"Saved {len(stocks)} stocks to database")
            return True

        except Exception as e:
            logger.error(f"Error saving stock list: {e}")
            return False

    def get_stock_list(self) -> List[str]:
        """
        Load stock list from database

        Returns:
            List of stock symbols, empty list if none saved
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT value FROM config WHERE key = "stock_list"')
            result = cursor.fetchone()

            conn.close()

            if result and result[0]:
                stocks = [s.strip() for s in result[0].split(',') if s.strip()]
                logger.info(f"Loaded {len(stocks)} stocks from database")
                return stocks
            else:
                logger.info("No saved stock list found in database")
                return []

        except Exception as e:
            logger.error(f"Error loading stock list: {e}")
            return []

    def save_scanner_state(self, active: bool) -> bool:
        """
        Save scanner active state to database

        Args:
            active: Whether scanner is active

        Returns:
            bool: Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO config (key, value, updated_at)
                VALUES ('scanner_active', ?, CURRENT_TIMESTAMP)
            ''', ('1' if active else '0',))

            conn.commit()
            conn.close()

            logger.info(f"Saved scanner state: {'Active' if active else 'Inactive'}")
            return True

        except Exception as e:
            logger.error(f"Error saving scanner state: {e}")
            return False

    def get_scanner_state(self) -> bool:
        """
        Load scanner active state from database

        Returns:
            bool: Scanner active state (default False)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT value FROM config WHERE key = "scanner_active"')
            result = cursor.fetchone()

            conn.close()

            if result and result[0]:
                active = result[0] == '1'
                logger.info(f"Loaded scanner state: {'Active' if active else 'Inactive'}")
                return active
            else:
                logger.info("No saved scanner state found, defaulting to inactive")
                return False

        except Exception as e:
            logger.error(f"Error loading scanner state: {e}")
            return False
