from apscheduler.schedulers.blocking import BlockingScheduler

from stratos.backend.ingestion.crypto import run_crypto_ingestion
from stratos.backend.ingestion.macro import run_macro_ingestion
from stratos.backend.ingestion.market import run_market_ingestion
from stratos.backend.ingestion.news import run_news_ingestion
from stratos.backend.narrative.engine import run_narrative_job
from stratos.backend.portfolio.analytics import run_portfolio_job
from stratos.backend.processing.analytics import run_analytics_job
from stratos.backend.signals.assets import run_asset_signal_job
from stratos.backend.signals.macro import run_macro_signal_job
from stratos.database.db import init_db


def refresh_signals() -> None:
    run_analytics_job()
    run_macro_signal_job()
    run_asset_signal_job()
    run_narrative_job()
    run_portfolio_job()


def build_scheduler() -> BlockingScheduler:
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(run_market_ingestion, "interval", minutes=5, id="market_data", replace_existing=True)
    scheduler.add_job(run_crypto_ingestion, "interval", minutes=2, id="crypto", replace_existing=True)
    scheduler.add_job(run_macro_ingestion, "cron", hour=6, minute=0, id="macro_fred", replace_existing=True)
    scheduler.add_job(run_news_ingestion, "interval", minutes=10, id="news_rss", replace_existing=True)
    scheduler.add_job(refresh_signals, "interval", minutes=15, id="signals", replace_existing=True)
    return scheduler


def main() -> None:
    init_db()
    scheduler = build_scheduler()
    scheduler.start()


if __name__ == "__main__":
    main()
