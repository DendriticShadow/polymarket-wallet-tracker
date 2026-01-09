"""
Data collection service for fetching and storing Polymarket data
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from app.db.models import Wallet, Market, Trade
from app.services.polymarket_client import PolymarketClient
from app.services.wallet_classifier import WalletClassifier

logger = logging.getLogger(__name__)


class DataCollector:
    """Service for collecting and storing Polymarket data"""

    def __init__(self, db: Session):
        self.db = db
        self.client = PolymarketClient()
        self.wallet_classifier = WalletClassifier(db)

    def parse_trade_data(self, trade_data: dict) -> Optional[dict]:
        """
        Parse trade data from Polymarket API

        Args:
            trade_data: Raw trade data from API

        Returns:
            Parsed trade dictionary or None if invalid
        """
        try:
            # Extract fields based on actual Polymarket API structure
            tx_hash = trade_data.get('transactionHash')
            wallet_address = trade_data.get('proxyWallet')

            # Use slug as market_id (more stable than asset ID)
            market_id = trade_data.get('slug') or trade_data.get('eventSlug')

            # Skip if missing required fields
            if not tx_hash or not wallet_address or not market_id:
                logger.debug(f"Skipping trade with missing required fields")
                return None

            # Parse trade type
            side = trade_data.get('side', '').upper()
            trade_type = 'buy' if side == 'BUY' else 'sell'

            # Parse amounts
            size = float(trade_data.get('size', 0))
            price = float(trade_data.get('price', 0))

            # Calculate shares (size * price for the token amount)
            shares = size
            token_amount = size  # In USDC/USD

            # Parse timestamp
            timestamp = datetime.fromtimestamp(
                int(trade_data.get('timestamp', 0))
            ) if trade_data.get('timestamp') else datetime.utcnow()

            parsed = {
                'tx_hash': tx_hash,
                'wallet_address': wallet_address,
                'market_id': market_id,
                'trade_type': trade_type,
                'token_amount': token_amount,
                'shares': shares,
                'price': price,
                'timestamp': timestamp
            }

            # Also extract embedded market data for later storage
            parsed['market_data'] = {
                'market_id': market_id,
                'title': trade_data.get('title', ''),
                'category': trade_data.get('category', ''),
                'slug': market_id,
                'asset': trade_data.get('asset'),
                'conditionId': trade_data.get('conditionId'),
                'outcome': trade_data.get('outcome'),
                'icon': trade_data.get('icon')
            }

            return parsed
        except Exception as e:
            logger.error(f"Error parsing trade data: {e}")
            return None

    def store_trade(self, trade_data: dict) -> Optional[Trade]:
        """
        Store a trade in the database

        Args:
            trade_data: Parsed trade dictionary

        Returns:
            Trade object or None if already exists
        """
        # Check if trade already exists
        existing_trade = self.db.query(Trade).filter(
            Trade.tx_hash == trade_data['tx_hash']
        ).first()

        if existing_trade:
            return None

        # Create or update wallet
        self.wallet_classifier.create_or_update_wallet(
            trade_data['wallet_address'],
            trade_data['timestamp']
        )

        # Create trade (exclude market_data which is not part of Trade model)
        trade_fields = {k: v for k, v in trade_data.items() if k != 'market_data'}
        trade = Trade(**trade_fields)
        self.db.add(trade)

        try:
            self.db.commit()
            logger.debug(f"Stored trade {trade_data['tx_hash']}")
            return trade
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing trade: {e}")
            return None

    def parse_market_data(self, market_data: dict) -> Optional[dict]:
        """
        Parse market data from Polymarket API

        Args:
            market_data: Raw market data from API

        Returns:
            Parsed market dictionary or None if invalid
        """
        try:
            # Extract market ID
            market_id = market_data.get('id') or market_data.get('conditionId')
            if not market_id:
                logger.debug("Skipping market with no ID")
                return None

            # Parse dates
            end_date = None
            if market_data.get('endDate'):
                try:
                    end_date = datetime.fromisoformat(
                        market_data['endDate'].replace('Z', '+00:00')
                    )
                except:
                    pass

            resolution_date = None
            if market_data.get('resolutionDate'):
                try:
                    resolution_date = datetime.fromisoformat(
                        market_data['resolutionDate'].replace('Z', '+00:00')
                    )
                except:
                    pass

            # Extract title and description
            title = market_data.get('question') or market_data.get('title', '')
            description = market_data.get('description', '')

            # Extract category
            category = market_data.get('category', '')

            # Extract volume and liquidity
            volume = market_data.get('volume') or market_data.get('liquidity', 0)
            try:
                total_volume = float(volume)
            except:
                total_volume = 0

            return {
                'market_id': str(market_id),
                'title': title,
                'description': description,
                'category': category,
                'end_date': end_date,
                'resolution_date': resolution_date,
                'resolved': market_data.get('closed', False) or market_data.get('resolved', False),
                'outcome': market_data.get('outcome'),
                'total_volume': total_volume,
                'holder_count': market_data.get('participants'),
                'market_metadata': market_data
            }
        except Exception as e:
            logger.error(f"Error parsing market data: {e}")
            return None

    def store_market(self, market_data: dict) -> Optional[Market]:
        """
        Store or update a market in the database

        Args:
            market_data: Parsed market dictionary

        Returns:
            Market object
        """
        # Check if market exists
        market = self.db.query(Market).filter(
            Market.market_id == market_data['market_id']
        ).first()

        if market:
            # Update existing market
            for key, value in market_data.items():
                if key != 'market_id':
                    setattr(market, key, value)
        else:
            # Create new market
            market = Market(**market_data)
            self.db.add(market)

        try:
            self.db.commit()
            logger.debug(f"Stored market {market_data['market_id']}")
            return market
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing market: {e}")
            return None

    def collect_recent_trades(self, limit: int = 1000) -> int:
        """
        Fetch and store recent trades

        Args:
            limit: Maximum number of trades to fetch

        Returns:
            Number of new trades stored
        """
        logger.info(f"Fetching {limit} recent trades...")

        trades_data = self.client.fetch_recent_trades(limit=limit)

        if not trades_data:
            logger.warning("No trades fetched")
            return 0

        new_trades = 0
        for trade_data in trades_data:
            parsed = self.parse_trade_data(trade_data)
            if parsed:
                # Create market from embedded trade data
                if parsed.get('market_data'):
                    market_info = parsed['market_data']
                    simple_market = {
                        'market_id': market_info['market_id'],
                        'title': market_info['title'],
                        'category': market_info.get('category', ''),
                        'description': '',
                        'end_date': None,
                        'resolution_date': None,
                        'resolved': False,
                        'outcome': market_info.get('outcome'),
                        'total_volume': 0,
                        'holder_count': None,
                        'market_metadata': market_info
                    }
                    self.store_market(simple_market)

                # Store trade
                if self.store_trade(parsed):
                    new_trades += 1

        logger.info(f"Stored {new_trades} new trades")
        return new_trades

    def ensure_market_exists(self, market_id: str) -> Optional[Market]:
        """
        Ensure a market exists in the database, fetch if needed

        Args:
            market_id: Market identifier

        Returns:
            Market object or None
        """
        market = self.db.query(Market).filter(
            Market.market_id == market_id
        ).first()

        if not market:
            # Fetch from API
            market_data = self.client.fetch_market_metadata(market_id)
            if market_data:
                parsed = self.parse_market_data(market_data)
                if parsed:
                    market = self.store_market(parsed)

        return market

    def collect_markets(self, limit: int = 100, active_only: bool = True) -> int:
        """
        Fetch and store markets

        Args:
            limit: Maximum number of markets to fetch
            active_only: Only fetch active markets

        Returns:
            Number of markets stored/updated
        """
        logger.info(f"Fetching markets (active_only={active_only})...")

        markets_data = self.client.fetch_all_markets(
            limit=limit,
            active=active_only
        )

        if not markets_data:
            logger.warning("No markets fetched")
            return 0

        stored_count = 0
        for market_data in markets_data:
            parsed = self.parse_market_data(market_data)
            if parsed:
                if self.store_market(parsed):
                    stored_count += 1

        logger.info(f"Stored/updated {stored_count} markets")
        return stored_count

    def update_wallet_statistics(self) -> int:
        """
        Update statistics for all wallets

        Returns:
            Number of wallets updated
        """
        wallets = self.db.query(Wallet).all()

        for wallet in wallets:
            self.wallet_classifier.update_wallet_stats(wallet.address)

        logger.info(f"Updated {len(wallets)} wallet statistics")
        return len(wallets)
