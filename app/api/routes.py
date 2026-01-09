"""
API routes for Polymarket Tracker
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.database import get_db
from app.db.models import Wallet, Market, Trade, Alert, Position
from app.api import schemas

router = APIRouter()


# Wallets endpoints
@router.get("/wallets", response_model=List[schemas.WalletResponse])
def list_wallets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    fresh_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """List all tracked wallets"""
    query = db.query(Wallet)

    if fresh_only:
        query = query.filter(Wallet.is_fresh == True)

    wallets = query.offset(skip).limit(limit).all()
    return wallets


@router.get("/wallets/{address}", response_model=schemas.WalletDetailResponse)
def get_wallet(address: str, db: Session = Depends(get_db)):
    """Get wallet details"""
    wallet = db.query(Wallet).filter(Wallet.address == address).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return wallet


@router.get("/wallets/{address}/trades", response_model=List[schemas.TradeResponse])
def get_wallet_trades(
    address: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get wallet trade history"""
    trades = db.query(Trade).filter(
        Trade.wallet_address == address
    ).order_by(desc(Trade.timestamp)).offset(skip).limit(limit).all()

    return trades


@router.get("/wallets/{address}/positions", response_model=List[schemas.PositionResponse])
def get_wallet_positions(
    address: str,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get current positions for a wallet"""
    query = db.query(Position).filter(Position.wallet_address == address)

    if status:
        query = query.filter(Position.status == status)

    positions = query.all()
    return positions


# Markets endpoints
@router.get("/markets", response_model=List[schemas.MarketResponse])
def list_markets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resolved: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all markets"""
    query = db.query(Market)

    if resolved is not None:
        query = query.filter(Market.resolved == resolved)

    if category:
        query = query.filter(Market.category == category)

    markets = query.offset(skip).limit(limit).all()
    return markets


@router.get("/markets/{market_id}", response_model=schemas.MarketDetailResponse)
def get_market(market_id: str, db: Session = Depends(get_db)):
    """Get market details"""
    market = db.query(Market).filter(Market.market_id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    return market


@router.get("/markets/{market_id}/trades", response_model=List[schemas.TradeResponse])
def get_market_trades(
    market_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get trades for a market"""
    trades = db.query(Trade).filter(
        Trade.market_id == market_id
    ).order_by(desc(Trade.timestamp)).offset(skip).limit(limit).all()

    return trades


# Alerts endpoints
@router.get("/alerts", response_model=List[schemas.AlertResponse])
def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    min_risk_score: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    """List all alerts (flagged activity)"""
    query = db.query(Alert)

    if status:
        query = query.filter(Alert.status == status)

    if min_risk_score is not None:
        query = query.filter(Alert.risk_score >= min_risk_score)

    alerts = query.order_by(desc(Alert.flagged_at)).offset(skip).limit(limit).all()
    return alerts


@router.get("/alerts/{alert_id}", response_model=schemas.AlertDetailResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get alert details"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.post("/alerts/{alert_id}/dismiss")
def dismiss_alert(alert_id: int, db: Session = Depends(get_db)):
    """Dismiss a false positive alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = "dismissed"
    db.commit()

    return {"message": "Alert dismissed", "alert_id": alert_id}


# Trades endpoints
@router.get("/trades", response_model=List[schemas.TradeResponse])
def list_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List recent trades (live feed)"""
    trades = db.query(Trade).order_by(
        desc(Trade.timestamp)
    ).offset(skip).limit(limit).all()

    return trades


@router.get("/trades/{tx_hash}", response_model=schemas.TradeDetailResponse)
def get_trade(tx_hash: str, db: Session = Depends(get_db)):
    """Get trade details"""
    trade = db.query(Trade).filter(Trade.tx_hash == tx_hash).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    return trade


# Analytics endpoints
@router.get("/analytics/summary", response_model=schemas.AnalyticsSummaryResponse)
def get_analytics_summary(db: Session = Depends(get_db)):
    """Dashboard statistics"""
    from sqlalchemy import func

    total_wallets = db.query(func.count(Wallet.address)).scalar()
    fresh_wallets = db.query(func.count(Wallet.address)).filter(
        Wallet.is_fresh == True
    ).scalar()
    total_trades = db.query(func.count(Trade.id)).scalar()
    total_alerts = db.query(func.count(Alert.id)).scalar()
    pending_alerts = db.query(func.count(Alert.id)).filter(
        Alert.status == 'pending'
    ).scalar()

    return {
        "total_wallets": total_wallets or 0,
        "fresh_wallets": fresh_wallets or 0,
        "total_trades": total_trades or 0,
        "total_alerts": total_alerts or 0,
        "pending_alerts": pending_alerts or 0
    }
