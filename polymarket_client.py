"""
Polymarket API client for fetching data
"""
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class PolymarketClient:
    """Client for interacting with Polymarket APIs"""

    def __init__(self):
        self.data_api_url = settings.POLYMARKET_DATA_API
        self.gamma_api_url = settings.POLYMARKET_GAMMA_API
        self.clob_api_url = settings.POLYMARKET_CLOB_API
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PolymarketTracker/0.1.0'
        })

    def fetch_recent_trades(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Fetch recent trades from Polymarket

        Args:
            limit: Maximum number of trades to fetch
            offset: Offset for pagination

        Returns:
            List of trade dictionaries
        """
        try:
            url = f"{self.data_api_url}/trades"
            params = {
                "limit": limit,
                "offset": offset
            }
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching trades: {e}")
            return []

    def fetch_market_metadata(self, market_id: str) -> Optional[Dict[str, Any]]:
        """
        Get market details from Gamma API

        Args:
            market_id: Market identifier

        Returns:
            Market metadata dictionary or None if not found
        """
        try:
            url = f"{self.gamma_api_url}/markets/{market_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching market {market_id}: {e}")
            return None

    def fetch_all_markets(
        self,
        limit: int = 100,
        offset: int = 0,
        active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of markets

        Args:
            limit: Maximum number of markets to fetch
            offset: Offset for pagination
            active: Filter for active markets only

        Returns:
            List of market dictionaries
        """
        try:
            url = f"{self.gamma_api_url}/markets"
            params = {
                "limit": limit,
                "offset": offset
            }
            if active is not None:
                params["active"] = str(active).lower()

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching markets: {e}")
            return []

    def fetch_wallet_activity(
        self,
        wallet_address: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get wallet activity history

        Args:
            wallet_address: Wallet address
            limit: Maximum number of activities to fetch

        Returns:
            List of activity dictionaries
        """
        try:
            url = f"{self.data_api_url}/activity"
            params = {
                "address": wallet_address,
                "limit": limit
            }
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching wallet activity for {wallet_address}: {e}")
            return []

    def fetch_current_prices(self, market_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current odds/prices for a market

        Args:
            market_id: Market identifier

        Returns:
            Price data or None
        """
        try:
            url = f"{self.clob_api_url}/prices"
            params = {"market_id": market_id}
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching prices for market {market_id}: {e}")
            return None

    def fetch_positions(
        self,
        wallet_address: str,
        market_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get wallet positions

        Args:
            wallet_address: Wallet address
            market_id: Optional market filter

        Returns:
            List of position dictionaries
        """
        try:
            url = f"{self.data_api_url}/positions"
            params = {"address": wallet_address}
            if market_id:
                params["market_id"] = market_id

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching positions for {wallet_address}: {e}")
            return []
