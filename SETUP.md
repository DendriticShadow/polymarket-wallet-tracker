# Polymarket Tracker - Setup Guide

## Quick Start with Docker (Recommended)

The fastest way to get started is using Docker Compose:

```bash
cd polymarket-tracker

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker ps
```

The following services will be running:
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL Database**: localhost:5432
- **Redis**: localhost:6379
- **Data Collector**: Background service
- **Pattern Detector**: Background service

## Manual Setup (For Development)

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Step 1: Install Dependencies

```bash
cd polymarket-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

Required settings:
- `DATABASE_URL`: PostgreSQL connection string
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database credentials
- `REDIS_URL`: Redis connection string

### Step 3: Initialize Database

Make sure PostgreSQL is running, then:

```bash
# Create database
createdb polymarket_tracker

# Initialize tables
python scripts/init_db.py
```

Or manually run the schema:
```bash
psql -U admin -d polymarket_tracker -f schema.sql
```

### Step 4: Run Services

You need to run three services (in separate terminals):

**Terminal 1 - API Server:**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Data Collector:**
```bash
python scripts/collector.py
```

**Terminal 3 - Pattern Detector:**
```bash
python scripts/detector.py
```

Or use the Makefile:
```bash
# Terminal 1
make run-api

# Terminal 2
make run-collector

# Terminal 3
make run-detector
```

## Verifying the Setup

### 1. Check API Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. View API Documentation

Open your browser to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Check Database

```bash
# Connect to database
psql -U admin -d polymarket_tracker

# Check tables
\dt

# View wallets
SELECT * FROM wallets LIMIT 5;

# View recent trades
SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;

# View alerts
SELECT * FROM alerts ORDER BY flagged_at DESC LIMIT 10;
```

### 4. Monitor Logs

**Docker:**
```bash
docker-compose logs -f collector
docker-compose logs -f detector
docker-compose logs -f api
```

**Manual:**
Check the terminal output where you started each service.

## Testing the Pattern Detection

### 1. Wait for Data Collection

The collector runs every 5 minutes by default. Wait for at least one cycle:

```bash
# Check collector logs for:
# "Collected X new trades"
# "Updated X markets"
```

### 2. Check for Alerts

```bash
# Using API
curl http://localhost:8000/api/alerts

# Using database
psql -U admin -d polymarket_tracker -c "SELECT * FROM alerts ORDER BY risk_score DESC LIMIT 10;"
```

### 3. View Dashboard Statistics

```bash
curl http://localhost:8000/api/analytics/summary
```

Expected response:
```json
{
  "total_wallets": 123,
  "fresh_wallets": 45,
  "total_trades": 5678,
  "total_alerts": 12,
  "pending_alerts": 8
}
```

## Configuration Tuning

### Adjust Detection Sensitivity

Edit `.env`:

```bash
# Lower threshold = more alerts (20 is default)
SUSPICIOUS_THRESHOLD=15

# Fresh wallet criteria
FRESH_WALLET_DAYS=30          # Wallet age in days
FRESH_WALLET_MAX_TXS=20       # Max transaction count
FRESH_WALLET_MAX_POSITION=10000  # Max position size in USD
```

### Adjust Collection Frequency

```bash
# Collection interval in seconds (300 = 5 minutes)
COLLECTION_INTERVAL_SECONDS=300

# Number of trades to fetch per cycle
TRADES_FETCH_LIMIT=1000
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U admin -d polymarket_tracker -c "SELECT 1;"
```

### API Not Starting

```bash
# Check port is not in use
lsof -i :8000

# Check database is accessible
python -c "from app.db.database import engine; print(engine.connect())"
```

### No Data Being Collected

1. Check Polymarket API is accessible:
```bash
curl https://data-api.polymarket.com/trades?limit=1
```

2. Check collector logs for errors

3. Verify network connectivity

### No Alerts Being Generated

1. Check if trades are being stored:
```bash
psql -U admin -d polymarket_tracker -c "SELECT COUNT(*) FROM trades;"
```

2. Verify detection threshold isn't too high

3. Check detector logs for errors

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_pattern_detector.py -v

# With coverage
pytest tests/ --cov=app
```

### Code Formatting

```bash
# Format code
black app/ scripts/

# Check types
mypy app/
```

### Database Migrations

If you need to modify the schema:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Production Deployment

### Security Checklist

- [ ] Change default database passwords
- [ ] Use strong `DB_PASSWORD` in `.env`
- [ ] Configure CORS properly in `app/main.py`
- [ ] Set `DEBUG=False` in production
- [ ] Use environment-specific `.env` files
- [ ] Enable PostgreSQL SSL connections
- [ ] Set up firewall rules
- [ ] Use reverse proxy (nginx/Traefik)
- [ ] Enable HTTPS with Let's Encrypt
- [ ] Set up monitoring and alerting

### Recommended Setup

1. Use managed PostgreSQL (AWS RDS, DigitalOcean, etc.)
2. Deploy with Docker Compose or Kubernetes
3. Set up log aggregation (ELK, Loki, etc.)
4. Configure backup strategy for database
5. Set up health check monitoring
6. Use environment variables for secrets

## Support

For issues or questions:
- Check logs: `docker-compose logs -f` or terminal output
- Review API docs: http://localhost:8000/docs
- Check database: `psql -U admin -d polymarket_tracker`

## Next Steps

1. Build a frontend dashboard (React/Next.js)
2. Add WebSocket support for real-time updates
3. Implement notification system (email/Discord/Telegram)
4. Add machine learning model for better detection
5. Implement news correlation analysis
6. Add social graph analysis
