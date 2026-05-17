from datetime import UTC, datetime

import feedparser

from stratos.database.db import connect, upsert_job
from stratos.logging_config import get_logger

LOGGER = get_logger(__name__)
FEEDS = {
    "Reuters Markets": "https://feeds.reuters.com/reuters/marketsNews",
    "CNBC Markets": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
}


def run_news_ingestion() -> None:
    now = datetime.now(UTC).isoformat()
    inserted = 0
    try:
        with connect() as conn:
            for source, url in FEEDS.items():
                feed = feedparser.parse(url)
                for entry in feed.entries[:20]:
                    cursor = conn.execute(
                        """
                        INSERT OR IGNORE INTO headlines(source, title, link, published_at, inserted_at)
                        VALUES(?, ?, ?, ?, ?)
                        """,
                        (source, entry.get("title", ""), entry.get("link"), entry.get("published", ""), now),
                    )
                    inserted += cursor.rowcount
        upsert_job("news_rss", "success", now, f"{inserted} new headlines")
    except Exception as exc:
        LOGGER.exception("News ingestion failed")
        upsert_job("news_rss", "failed", now, str(exc))
        raise
