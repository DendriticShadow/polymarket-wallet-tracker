"""
Tests for pattern detection engine
"""
import pytest
from datetime import datetime, timedelta
from app.services.pattern_detector import PatternDetector
from app.db.models import Market


def test_score_position_size():
    """Test position size scoring"""
    detector = PatternDetector(None)

    assert detector.score_position_size(60000) == 10
    assert detector.score_position_size(25000) == 8
    assert detector.score_position_size(15000) == 6
    assert detector.score_position_size(7000) == 4
    assert detector.score_position_size(3000) == 0


def test_score_payout_ratio():
    """Test payout ratio scoring"""
    detector = PatternDetector(None)

    assert detector.score_payout_ratio(0.20) == 8  # 5:1 odds
    assert detector.score_payout_ratio(0.30) == 5
    assert detector.score_payout_ratio(0.45) == 3
    assert detector.score_payout_ratio(0.60) == 0


def test_score_market_niche():
    """Test market niche scoring"""
    detector = PatternDetector(None)

    # Create a niche market
    market = Market(
        market_id="test-1",
        title="Test Market",
        category="politics-international",
        total_volume=30000,
        holder_count=50,
        resolved=False
    )

    score = detector.score_market_niche(market)
    assert score > 0  # Should have some niche score


def test_score_time_to_resolution():
    """Test time to resolution scoring"""
    detector = PatternDetector(None)

    now = datetime.utcnow()

    # Create market resolving in 1 day
    market = Market(
        market_id="test-2",
        title="Test Market",
        resolution_date=now + timedelta(days=1),
        resolved=False
    )

    score = detector.score_time_to_resolution(market, now)
    assert score == 10  # Very suspicious

    # Market resolving in 4 days
    market.resolution_date = now + timedelta(days=4)
    score = detector.score_time_to_resolution(market, now)
    assert score == 5
