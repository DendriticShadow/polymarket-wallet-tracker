"""
Wallet classification service
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models import Wallet, Trade
from app.core.config import settings


class WalletClassifier:
    """Service for classifying and tracking wallets"""

    def __init__(self, db: Session):
        self.db = db

    def is_fresh_wallet(self, wallet_address: str) -> bool:
        """
        Determine if a wallet is 'fresh' (recently created with low activity)

        Criteria for 'fresh' wallet:
        - First transaction < 30 days ago (configurable)
        - Total lifetime transactions < 20 (configurable)
        - No previous large positions (> $10k) (configurable)

        Args:
            wallet_address: Wallet address to check

        Returns:
            True if wallet is fresh, False otherwise
        """
        wallet = self.db.query(Wallet).filter(
            Wallet.address == wallet_address
        ).first()

        if not wallet:
            # If wallet doesn't exist in our DB yet, consider it fresh
            return True

        # Check age
        days_old = (datetime.utcnow() - wallet.first_seen_date).days
        is_new = days_old < settings.FRESH_WALLET_DAYS

        # Check activity level
        is_low_activity = wallet.total_trades < settings.FRESH_WALLET_MAX_TXS

        # Check historical position size
        max_position = self.get_max_historical_position(wallet_address)
        is_small_history = max_position < settings.FRESH_WALLET_MAX_POSITION

        return is_new and is_low_activity and is_small_history

    def get_max_historical_position(self, wallet_address: str) -> float:
        """
        Get the maximum historical position size for a wallet

        Args:
            wallet_address: Wallet address

        Returns:
            Maximum position size in USD
        """
        result = self.db.query(
            func.max(Trade.token_amount)
        ).filter(
            Trade.wallet_address == wallet_address
        ).scalar()

        return float(result) if result else 0.0

    def get_wallet_stats(self, wallet_address: str) -> dict:
        """
        Get comprehensive wallet statistics

        Args:
            wallet_address: Wallet address

        Returns:
            Dictionary with wallet statistics
        """
        wallet = self.db.query(Wallet).filter(
            Wallet.address == wallet_address
        ).first()

        if not wallet:
            return {
                "exists": False,
                "is_fresh": True,
                "total_trades": 0,
                "total_volume": 0,
                "lifetime_pnl": 0,
                "days_active": 0
            }

        days_active = (datetime.utcnow() - wallet.first_seen_date).days

        return {
            "exists": True,
            "is_fresh": wallet.is_fresh,
            "total_trades": wallet.total_trades,
            "total_volume": float(wallet.total_volume or 0),
            "lifetime_pnl": float(wallet.lifetime_pnl or 0),
            "days_active": days_active,
            "first_seen": wallet.first_seen_date,
            "last_activity": wallet.last_activity_date
        }

    def update_wallet_stats(self, wallet_address: str) -> None:
        """
        Recalculate and update wallet statistics

        Args:
            wallet_address: Wallet address
        """
        wallet = self.db.query(Wallet).filter(
            Wallet.address == wallet_address
        ).first()

        if not wallet:
            return

        # Count total trades
        total_trades = self.db.query(Trade).filter(
            Trade.wallet_address == wallet_address
        ).count()

        # Calculate total volume
        total_volume = self.db.query(
            func.sum(Trade.token_amount)
        ).filter(
            Trade.wallet_address == wallet_address
        ).scalar() or 0

        # Get last activity
        last_trade = self.db.query(Trade).filter(
            Trade.wallet_address == wallet_address
        ).order_by(Trade.timestamp.desc()).first()

        # Update wallet
        wallet.total_trades = total_trades
        wallet.total_volume = total_volume
        if last_trade:
            wallet.last_activity_date = last_trade.timestamp

        # Update fresh status
        wallet.is_fresh = self.is_fresh_wallet(wallet_address)

        self.db.commit()

    def create_or_update_wallet(
        self,
        wallet_address: str,
        timestamp: datetime
    ) -> Wallet:
        """
        Create new wallet or update existing one

        Args:
            wallet_address: Wallet address
            timestamp: Timestamp of activity

        Returns:
            Wallet object
        """
        wallet = self.db.query(Wallet).filter(
            Wallet.address == wallet_address
        ).first()

        if not wallet:
            # Create new wallet
            wallet = Wallet(
                address=wallet_address,
                first_seen_date=timestamp,
                last_activity_date=timestamp,
                is_fresh=True
            )
            self.db.add(wallet)
        else:
            # Update last activity
            if not wallet.last_activity_date or timestamp > wallet.last_activity_date:
                wallet.last_activity_date = timestamp

        self.db.commit()
        return wallet
