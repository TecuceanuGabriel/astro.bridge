import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from app.fetchers.space_track_fetcher import SpaceTrackFetcher
from app.core.db import SessionLocal

db = SessionLocal()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

space_track_username = os.environ.get("SPACE_TRACK_USERNAME")
space_track_password = os.environ.get("SPACE_TRACK_PASSWORD")


def run_sync_job():
    logger.info(f" Running satellite sync job at {datetime.utcnow()}")
    try:
        fetcher = SpaceTrackFetcher(space_track_username, space_track_password)
        fetcher.sync_TLEs(db)
        logger.info(" Satellite sync completed successfully.")
    except Exception as e:
        logger.error(f"❌ Sync job failed: {e}")


def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        run_sync_job,
        "interval",
        hours=6,
        id="satellite_sync",
        next_run_time=datetime.now(),
    )

    scheduler.start()
    logger.info(" Scheduler started: Sync job scheduled every 6 hours.")
