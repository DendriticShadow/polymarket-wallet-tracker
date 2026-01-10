"""
SQLAlchemy database models
"""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, DateTime,
    Text, ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Wallet(Base):
    """Wallet model"""
    __tablename__ = "wallets"

    address = Column(String(42), primary_key=True, index=True)
    first_seen_date = Column(DateTime, nullable=False)
    last_activity_date = Column(DateTime)
    total_trades = Column(Integer, default=0)
    total_volume = Column(Numeric(20, 2), default=0)
    lifetime_pnl = Column(Numeric(20, 2), default=0)
    is_fresh = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    trades = relationship("Trade", back_populates="wallet")
    positions = relationship("Position", back_populates="wallet")
    alerts = relationship("Alert", back_populates="wallet")


class Market(Base):
    """Market model"""
    __tablename__ = "markets"

    market_id = Column(String(100), primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    category = Column(String(100))
    end_date = Column(DateTime)
    resolution_date = Column(DateTime)
    resolved = Column(Boolean, default=False, index=True)
    outcome = Column(String(50))
    total_volume = Column(Numeric(20, 2))
    holder_count = Column(Integer)
    market_metadata = Column(JSON)  # Renamed from 'metadata' (reserved by SQLAlchemy)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    trades = relationship("Trade", back_populates="market")
    positions = relationship("Position", back_populates="market")
    alerts = relationship("Alert", back_populates="market")


class Trade(Base):
    """Trade model"""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tx_hash = Column(String(66), unique=True, nullable=False, index=True)
    wallet_address = Column(String(42), ForeignKey("wallets.address"), index=True)
    market_id = Column(String(100), ForeignKey("markets.market_id"), index=True)
    trade_type = Column(String(10))  # 'buy' or 'sell'
    token_amount = Column(Numeric(20, 8))  # USDC amount
    shares = Column(Numeric(20, 8))
    price = Column(Numeric(10, 8))  # Price per share
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    wallet = relationship("Wallet", back_populates="trades")
    market = relationship("Market", back_populates="trades")
    alerts = relationship("Alert", back_populates="trade")


class Position(Base):
    """Position model"""
    __tablename__ = "positions"
    __table_args__ = (
        Index('idx_wallet_market_unique', 'wallet_address', 'market_id', unique=True),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    wallet_address = Column(String(42), ForeignKey("wallets.address"), index=True)
    market_id = Column(String(100), ForeignKey("markets.market_id"), index=True)
    shares = Column(Numeric(20, 8))
    avg_purchase_price = Column(Numeric(10, 8))
    total_invested = Column(Numeric(20, 2))
    current_value = Column(Numeric(20, 2))
    unrealized_pnl = Column(Numeric(20, 2))
    status = Column(String(20), default='open', index=True)  # 'open', 'closed', 'resolved'
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    wallet = relationship("Wallet", back_populates="positions")
    market = relationship("Market", back_populates="positions")


class Alert(Base):
    """Alert model for flagged suspicious activity"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wallet_address = Column(String(42), ForeignKey("wallets.address"))
    market_id = Column(String(100), ForeignKey("markets.market_id"))
    trade_id = Column(Integer, ForeignKey("trades.id"))
    risk_score = Column(Integer, nullable=False, index=True)
    risk_factors = Column(JSON)  # Store individual score components
    position_size = Column(Numeric(20, 2))
    potential_payout = Column(Numeric(20, 2))
    market_resolution_date = Column(DateTime)
    status = Column(String(20), default='pending', index=True)  # 'pending', 'won', 'lost'
    actual_return = Column(Numeric(20, 2))
    flagged_at = Column(DateTime, default=func.now(), index=True)

    # Relationships
    wallet = relationship("Wallet", back_populates="alerts")
    market = relationship("Market", back_populates="alerts")
    trade = relationship("Trade", back_populates="alerts")
