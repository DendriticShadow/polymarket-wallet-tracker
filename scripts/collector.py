"""
Data collection script - Runs periodically to fetch Polymarket data
"""
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import SessionLocal
from app.services.data_collector import DataCollector
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def collect_data():
    """Single data collection cycle"""
    db = SessionLocal()

    try:
        collector = DataCollector(db)

        logger.info("=" * 60)
        logger.info(f"Starting data collection cycle at {datetime.now()}")

        # Collect recent trades
        new_trades = collector.collect_recent_trades(
            limit=settings.TRADES_FETCH_LIMIT
        )
        logger.info(f"Collected {new_trades} new trades")

        # Collect/update markets (less frequently)
        markets_updated = collector.collect_markets(limit=200, active_only=True)
        logger.info(f"Updated {markets_updated} markets")

        # Update wallet statistics
        wallets_updated = collector.update_wallet_statistics()
        logger.info(f"Updated {wallets_updated} wallet statistics")

        logger.info("Data collection cycle completed")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error in data collection: {e}", exc_info=True)
    finally:
        db.close()


def run_collection_loop():
    """Main loop - run periodically"""
    logger.info("Starting Polymarket data collector")
    logger.info(f"Collection interval: {settings.COLLECTION_INTERVAL_SECONDS} seconds")

    while True:
        try:
            collect_data()

            # Sleep until next collection
            logger.info(
                f"Sleeping for {settings.COLLECTION_INTERVAL_SECONDS} seconds..."
            )
            time.sleep(settings.COLLECTION_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            logger.info("Collection stopped by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            # Sleep for 1 minute before retrying
            time.sleep(60)


if __name__ == "__main__":
    run_collection_loop()
