"""
Pattern detection script - Analyzes trades for suspicious activity
"""
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import SessionLocal
from app.services.pattern_detector import PatternDetector
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def detect_patterns():
    """Single pattern detection cycle"""
    db = SessionLocal()

    try:
        detector = PatternDetector(db)

        logger.info("=" * 60)
        logger.info(f"Starting pattern detection cycle at {datetime.now()}")

        # Analyze trades from the last hour
        alerts_created = detector.analyze_recent_trades(hours=1)

        logger.info(f"Pattern detection completed - {alerts_created} new alerts")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error in pattern detection: {e}", exc_info=True)
    finally:
        db.close()


def run_detection_loop():
    """Main loop - run periodically"""
    logger.info("Starting Polymarket pattern detector")
    logger.info(f"Detection interval: {settings.COLLECTION_INTERVAL_SECONDS} seconds")
    logger.info(f"Suspicious threshold: {settings.SUSPICIOUS_THRESHOLD}")

    while True:
        try:
            detect_patterns()

            # Sleep until next detection cycle
            # Run slightly offset from collector to ensure fresh data
            sleep_time = settings.COLLECTION_INTERVAL_SECONDS + 30
            logger.info(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("Detection stopped by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            # Sleep for 1 minute before retrying
            time.sleep(60)


if __name__ == "__main__":
    run_detection_loop()
