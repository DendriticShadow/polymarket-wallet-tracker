-- Polymarket Tracker Database Schema

-- Wallets table
CREATE TABLE IF NOT EXISTS wallets (
    address VARCHAR(42) PRIMARY KEY,
    first_seen_date TIMESTAMP NOT NULL,
    last_activity_date TIMESTAMP,
    total_trades INTEGER DEFAULT 0,
    total_volume DECIMAL(20, 2) DEFAULT 0,
    lifetime_pnl DECIMAL(20, 2) DEFAULT 0,
    is_fresh BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Markets table
CREATE TABLE IF NOT EXISTS markets (
    market_id VARCHAR(100) PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category VARCHAR(100),
    end_date TIMESTAMP,
    resolution_date TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    outcome VARCHAR(50),
    total_volume DECIMAL(20, 2),
    holder_count INTEGER,
    market_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    tx_hash VARCHAR(66) UNIQUE NOT NULL,
    wallet_address VARCHAR(42) REFERENCES wallets(address),
    market_id VARCHAR(100) REFERENCES markets(market_id),
    trade_type VARCHAR(10),
    token_amount DECIMAL(20, 8),
    shares DECIMAL(20, 8),
    price DECIMAL(10, 8),
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Positions table
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    wallet_address VARCHAR(42) REFERENCES wallets(address),
    market_id VARCHAR(100) REFERENCES markets(market_id),
    shares DECIMAL(20, 8),
    avg_purchase_price DECIMAL(10, 8),
    total_invested DECIMAL(20, 2),
    current_value DECIMAL(20, 2),
    unrealized_pnl DECIMAL(20, 2),
    status VARCHAR(20) DEFAULT 'open',
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(wallet_address, market_id)
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    wallet_address VARCHAR(42) REFERENCES wallets(address),
    market_id VARCHAR(100) REFERENCES markets(market_id),
    trade_id INTEGER REFERENCES trades(id),
    risk_score INTEGER NOT NULL,
    risk_factors JSONB,
    position_size DECIMAL(20, 2),
    potential_payout DECIMAL(20, 2),
    market_resolution_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    actual_return DECIMAL(20, 2),
    flagged_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_trades_wallet ON trades(wallet_address);
CREATE INDEX IF NOT EXISTS idx_trades_market ON trades(market_id);
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_positions_wallet ON positions(wallet_address);
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);
CREATE INDEX IF NOT EXISTS idx_alerts_risk_score ON alerts(risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_flagged_at ON alerts(flagged_at DESC);
CREATE INDEX IF NOT EXISTS idx_wallets_is_fresh ON wallets(is_fresh);
CREATE INDEX IF NOT EXISTS idx_markets_resolved ON markets(resolved);
