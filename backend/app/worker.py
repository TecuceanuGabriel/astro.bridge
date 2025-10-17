import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from app.fetchers.sync import Syncer
from app.core.db import SessionLocal

db = SessionLocal()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_sync_job():
    logger.info(f" Running satellite sync job at {datetime.utcnow()}")
    try:
        syncer = Syncer(db)
        syncer.sync()
        logger.info(" Satellite sync completed successfully.")
    except Exception as e:
        logger.error(f"❌ Sync job failed: {e}")


def start_scheduler():
    scheduler = BackgroundScheduler()

    # scheduler.add_job(
    #     run_sync_job,
    #     "interval",
    #     hours=6,
    #     id="satellite_sync",
    #     next_run_time=datetime.now(),
    # )

    scheduler.start()
    logger.info(" Scheduler started: Sync job scheduled every 6 hours.")
