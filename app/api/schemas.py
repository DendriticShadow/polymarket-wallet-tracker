"""
Pydantic schemas for API request/response models
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from decimal import Decimal


class WalletResponse(BaseModel):
    """Wallet response schema"""
    address: str
    first_seen_date: datetime
    last_activity_date: Optional[datetime] = None
    total_trades: int
    total_volume: Decimal
    lifetime_pnl: Decimal
    is_fresh: bool

    class Config:
        from_attributes = True


class WalletDetailResponse(WalletResponse):
    """Detailed wallet response with additional info"""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MarketResponse(BaseModel):
    """Market response schema"""
    market_id: str
    title: str
    category: Optional[str] = None
    end_date: Optional[datetime] = None
    resolution_date: Optional[datetime] = None
    resolved: bool
    outcome: Optional[str] = None
    total_volume: Optional[Decimal] = None
    holder_count: Optional[int] = None

    class Config:
        from_attributes = True


class MarketDetailResponse(MarketResponse):
    """Detailed market response"""
    description: Optional[str] = None
    market_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TradeResponse(BaseModel):
    """Trade response schema"""
    id: int
    tx_hash: str
    wallet_address: str
    market_id: str
    trade_type: str
    token_amount: Decimal
    shares: Decimal
    price: Decimal
    timestamp: datetime

    class Config:
        from_attributes = True


class TradeDetailResponse(TradeResponse):
    """Detailed trade response"""
    created_at: datetime

    class Config:
        from_attributes = True


class PositionResponse(BaseModel):
    """Position response schema"""
    id: int
    wallet_address: str
    market_id: str
    shares: Decimal
    avg_purchase_price: Decimal
    total_invested: Decimal
    current_value: Optional[Decimal] = None
    unrealized_pnl: Optional[Decimal] = None
    status: str
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    """Alert response schema"""
    id: int
    wallet_address: str
    market_id: str
    trade_id: Optional[int] = None
    risk_score: int
    risk_factors: Optional[Dict[str, int]] = None
    position_size: Decimal
    potential_payout: Optional[Decimal] = None
    market_resolution_date: Optional[datetime] = None
    status: str
    flagged_at: datetime

    class Config:
        from_attributes = True


class AlertDetailResponse(AlertResponse):
    """Detailed alert response"""
    actual_return: Optional[Decimal] = None

    class Config:
        from_attributes = True


class AnalyticsSummaryResponse(BaseModel):
    """Analytics summary response"""
    total_wallets: int
    fresh_wallets: int
    total_trades: int
    total_alerts: int
    pending_alerts: int
