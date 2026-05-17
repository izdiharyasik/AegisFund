CREATE TABLE IF NOT EXISTS job_runs (
    job_name TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    last_success_at TEXT,
    last_run_at TEXT NOT NULL,
    message TEXT
);

CREATE TABLE IF NOT EXISTS latest_signals (
    asset TEXT PRIMARY KEY,
    asset_class TEXT NOT NULL,
    as_of TEXT NOT NULL,
    momentum REAL,
    relative_strength REAL,
    trend_status TEXT,
    volatility REAL,
    drawdown REAL,
    macro_alignment TEXT,
    conviction_score REAL,
    entry REAL,
    take_profit REAL,
    stop_loss REAL
);

CREATE TABLE IF NOT EXISTS macro_regime (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    as_of TEXT NOT NULL,
    regime TEXT NOT NULL,
    score REAL NOT NULL,
    summary TEXT,
    key_risks TEXT,
    opportunities TEXT
);

CREATE TABLE IF NOT EXISTS narratives (
    rule_name TEXT PRIMARY KEY,
    as_of TEXT NOT NULL,
    confidence REAL NOT NULL,
    narrative TEXT NOT NULL,
    implication TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS headlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    link TEXT,
    published_at TEXT,
    inserted_at TEXT NOT NULL,
    UNIQUE(source, title)
);

CREATE TABLE IF NOT EXISTS watchlist_assets (
    symbol TEXT PRIMARY KEY,
    label TEXT,
    group_name TEXT NOT NULL DEFAULT 'default',
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS portfolio_positions (
    symbol TEXT PRIMARY KEY,
    name TEXT,
    asset_class TEXT,
    market_value REAL NOT NULL,
    cost_basis REAL,
    target_weight REAL
);

CREATE TABLE IF NOT EXISTS portfolio_metrics (
    metric TEXT PRIMARY KEY,
    as_of TEXT NOT NULL,
    value REAL,
    label TEXT,
    detail TEXT
);
