"""
Pattern detection engine for identifying suspicious trading activity
"""
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session

from app.db.models import Wallet, Market, Trade, Alert
from app.services.wallet_classifier import WalletClassifier
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class PatternDetector:
    """Service for detecting suspicious trading patterns"""

    def __init__(self, db: Session):
        self.db = db
        self.wallet_classifier = WalletClassifier(db)
        self.suspicious_threshold = settings.SUSPICIOUS_THRESHOLD

    def score_position_size(self, trade_amount: float) -> int:
        """
        Score based on position size

        Large trades get higher scores

        Args:
            trade_amount: Trade amount in USD

        Returns:
            Score (0-10)
        """
        if trade_amount >= 50000:
            return 10
        elif trade_amount >= 20000:
            return 8
        elif trade_amount >= 10000:
            return 6
        elif trade_amount >= 5000:
            return 4
        else:
            return 0

    def score_market_niche(self, market: Market) -> int:
        """
        Score based on market niche characteristics

        Niche markets = low volume, specific topics

        Args:
            market: Market object

        Returns:
            Score (0-7)
        """
        score = 0

        # Low trading volume
        if market.total_volume and market.total_volume < 50000:
            score += 3

        # Specific categories (geopolitical, business, legal)
        niche_categories = [
            'politics-international',
            'business',
            'legal',
            'geopolitics'
        ]
        if market.category and market.category.lower() in niche_categories:
            score += 2

        # Few holders
        if market.holder_count and market.holder_count < 100:
            score += 2

        return score

    def score_payout_ratio(self, purchase_price: float) -> int:
        """
        Score based on potential payout ratio

        High payout potential = low probability purchases
        Example: Buying 'Yes' at $0.20 = 5:1 payout

        Args:
            purchase_price: Price per share (0-1)

        Returns:
            Score (0-8)
        """
        if purchase_price <= 0:
            return 0

        # If buying at < 25% probability = 4:1 or better odds
        if purchase_price < 0.25:
            return 8
        elif purchase_price < 0.35:
            return 5
        elif purchase_price < 0.50:
            return 3
        else:
            return 0

    def score_time_to_resolution(
        self,
        market: Market,
        trade_timestamp: datetime
    ) -> int:
        """
        Score based on time until market resolution

        Markets resolving very soon after purchase = suspicious

        Args:
            market: Market object
            trade_timestamp: When the trade occurred

        Returns:
            Score (0-10)
        """
        if not market.resolution_date:
            return 0

        days_until_resolution = (market.resolution_date - trade_timestamp).days

        if days_until_resolution <= 1:
            return 10
        elif days_until_resolution <= 3:
            return 7
        elif days_until_resolution <= 5:
            return 5
        elif days_until_resolution <= 7:
            return 3
        else:
            return 0

    def get_recent_trades_count(
        self,
        wallet_address: str,
        hours: int = 24
    ) -> int:
        """
        Get count of recent trades for a wallet

        Args:
            wallet_address: Wallet address
            hours: Time window in hours

        Returns:
            Number of trades
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        count = self.db.query(Trade).filter(
            Trade.wallet_address == wallet_address,
            Trade.timestamp >= cutoff_time
        ).count()

        return count

    def calculate_risk_score(
        self,
        trade: Trade,
        wallet: Wallet,
        market: Market
    ) -> Tuple[int, Dict[str, int]]:
        """
        Combine all heuristics into a single risk score

        Args:
            trade: Trade object
            wallet: Wallet object
            market: Market object

        Returns:
            Tuple of (total_score, risk_factors_dict)
        """
        # Only flag fresh wallets
        if not self.wallet_classifier.is_fresh_wallet(wallet.address):
            return 0, {}

        risk_factors = {}

        # Position size scoring
        size_score = self.score_position_size(float(trade.token_amount))
        risk_factors['position_size'] = size_score

        # Market niche scoring
        niche_score = self.score_market_niche(market)
        risk_factors['market_niche'] = niche_score

        # Payout ratio scoring
        payout_score = self.score_payout_ratio(float(trade.price))
        risk_factors['payout_ratio'] = payout_score

        # Time to resolution scoring
        timing_score = self.score_time_to_resolution(market, trade.timestamp)
        risk_factors['time_to_resolution'] = timing_score

        # Bonus for burst trading (multiple large trades in 24h)
        recent_trades = self.get_recent_trades_count(wallet.address, hours=24)
        burst_score = 0
        if recent_trades >= 3:
            burst_score = 5
        risk_factors['burst_trading'] = burst_score

        # Calculate total score
        total_score = sum(risk_factors.values())

        return total_score, risk_factors

    def create_alert(
        self,
        trade: Trade,
        risk_score: int,
        risk_factors: Dict[str, int],
        market: Market
    ) -> Alert:
        """
        Create an alert for suspicious activity

        Args:
            trade: Trade object
            risk_score: Calculated risk score
            risk_factors: Dictionary of individual score components
            market: Market object

        Returns:
            Created Alert object
        """
        # Calculate potential payout
        potential_payout = None
        if trade.price and trade.shares:
            # Simplified payout calculation
            cost = float(trade.token_amount)
            potential_payout = cost / float(trade.price) if float(trade.price) > 0 else cost

        alert = Alert(
            wallet_address=trade.wallet_address,
            market_id=trade.market_id,
            trade_id=trade.id,
            risk_score=risk_score,
            risk_factors=risk_factors,
            position_size=trade.token_amount,
            potential_payout=potential_payout,
            market_resolution_date=market.resolution_date,
            status='pending'
        )

        self.db.add(alert)
        self.db.commit()

        logger.warning(
            f"🚨 ALERT: Wallet {trade.wallet_address[:10]}... "
            f"Risk Score: {risk_score} "
            f"Position: ${float(trade.token_amount):,.2f} "
            f"Market: {market.title[:50]}"
        )

        return alert

    def analyze_trade(self, trade: Trade) -> Optional[Alert]:
        """
        Analyze a single trade for suspicious patterns

        Args:
            trade: Trade object to analyze

        Returns:
            Alert object if flagged, None otherwise
        """
        # Get wallet and market
        wallet = self.db.query(Wallet).filter(
            Wallet.address == trade.wallet_address
        ).first()

        market = self.db.query(Market).filter(
            Market.market_id == trade.market_id
        ).first()

        if not wallet or not market:
            return None

        # Calculate risk score
        risk_score, risk_factors = self.calculate_risk_score(trade, wallet, market)

        # Create alert if above threshold
        if risk_score >= self.suspicious_threshold:
            return self.create_alert(trade, risk_score, risk_factors, market)

        return None

    def analyze_recent_trades(self, hours: int = 1) -> int:
        """
        Run pattern detection on recent trades

        Args:
            hours: Time window to analyze

        Returns:
            Number of alerts created
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Get recent trades
        recent_trades = self.db.query(Trade).filter(
            Trade.timestamp >= cutoff_time
        ).all()

        alerts_created = 0
        for trade in recent_trades:
            # Check if already alerted
            existing_alert = self.db.query(Alert).filter(
                Alert.trade_id == trade.id
            ).first()

            if not existing_alert:
                alert = self.analyze_trade(trade)
                if alert:
                    alerts_created += 1

        logger.info(f"Analyzed {len(recent_trades)} trades, created {alerts_created} alerts")
        return alerts_created
