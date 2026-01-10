"""
Database initialization script
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import engine, Base
from app.db.models import Wallet, Market, Trade, Position, Alert
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database tables"""
    logger.info("Creating database tables...")

    Base.metadata.create_all(bind=engine)

    logger.info("✓ Database tables created successfully")


if __name__ == "__main__":
    init_database()
