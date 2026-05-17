from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG_DIR = ROOT / "configs"
DATABASE_DIR = ROOT / "database"
CACHE_DIR = ROOT / "cache"
LOG_DIR = ROOT / "logs"
DB_PATH = DATABASE_DIR / "stratos.sqlite"
MARKET_PARQUET = CACHE_DIR / "market_timeseries.parquet"
ANALYTICS_PARQUET = CACHE_DIR / "analytics_timeseries.parquet"

for path in (DATABASE_DIR, CACHE_DIR, LOG_DIR):
    path.mkdir(parents=True, exist_ok=True)
